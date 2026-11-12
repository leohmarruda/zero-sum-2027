"""HTTP routes — game lifecycle and turns (spec.md §2.11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_game_service, get_turn_service
from app.api.schemas import (
    AdjudicationOut,
    CategoryScoresOut,
    ContentOut,
    CreateGameRequest,
    GameOut,
    HistoryOut,
    HistoryPointOut,
    MoveOut,
    OffAskOut,
    OffAskRequest,
    ResolveOut,
    SeatOut,
    SubmitMoveRequest,
    TurnOut,
)
from app.domain.roles import SeatRole, is_playable
from app.domain.types import CategoryScores, TurnScores
from app.llm.prompts import build_narrator_intro, content_bundle
from app.models import Game, GameStatus, PlayerType
from app.services.game_service import GameService, SeatConfig
from app.services.turn_service import ResolveResult, TurnService

router = APIRouter()


def _resolve_out(result: ResolveResult, turn_number: int, data: dict) -> ResolveOut:
    adj = result.adjudication
    turn_payload = TurnOut(
        turn_number=turn_number,
        moves=[
            MoveOut(
                seat_role=m.seat_role.value,  # type: ignore[arg-type]
                move_text=m.move_text,
                turn_number=m.turn_number,
            )
            for m in data["moves"]
        ],
        adjudication=(
            AdjudicationOut(
                turn_number=adj.turn_number,
                world_narrative=adj.world_narrative,
                world_state_digest=adj.world_state_digest or "",
                seat_feedback=adj.seat_feedback,
            )
            if adj is not None
            else None
        ),
        scores=_scores_out(result.scores if result.scores is not None else data["scores"]),
        deltas=data.get("deltas"),
    )
    return ResolveOut(
        game=_game_out(result.game, result.scores),
        turn=turn_payload,
        already_resolved=result.already_resolved,
        rejected=result.rejected,
        rejection_reason=result.rejection_reason,
    )

def _scores_out(scores: TurnScores | None) -> dict[str, CategoryScoresOut] | None:
    if scores is None:
        return None
    return {role: CategoryScoresOut(**cats.as_dict()) for role, cats in scores.items()}


def _scores_from_game(game: Game) -> TurnScores | None:
    by_turn: dict[int, TurnScores] = {}
    for row in game.scores:
        if not is_playable(row.seat_role):
            continue
        by_turn.setdefault(row.turn_number, {})[row.seat_role.value] = CategoryScores(
            sm=row.sm, rc=row.rc, ic=row.ic, pc=row.pc, cs=row.cs
        )
    if not by_turn:
        return None
    if game.status == GameStatus.ended:
        play = [t for t in by_turn if t >= 1]
        turn = max(play) if play else 0
    else:
        turn = max(game.current_turn - 1, 0)
        if turn not in by_turn:
            turn = 0
    return by_turn.get(turn)


def _game_out(
    game: Game,
    scores: TurnScores | None = None,
    *,
    narrator_intro: str | None = None,
    locale: str | None = None,
) -> GameOut:
    if narrator_intro is None:
        roles = [s.role.value for s in game.seats if is_playable(s.role)]
        narrator_intro = build_narrator_intro(roles, locale)
    return GameOut(
        id=game.id,
        status=game.status.value,  # type: ignore[arg-type]
        current_turn=game.current_turn,
        turn_cap=game.turn_cap,
        humanity_win_turn=game.humanity_win_turn,
        winner=game.winner,
        ending=game.ending,
        epilogue=game.epilogue,
        ended_at=game.ended_at,
        seats=[
            SeatOut(
                role=s.role.value,  # type: ignore[arg-type]
                player_type=s.player_type.value,  # type: ignore[arg-type]
                model=s.model,
                temperature=s.temperature,
                display_name=s.display_name,
            )
            for s in sorted(game.seats, key=lambda s: s.role.value)
        ],
        current_scores=_scores_out(
            scores if scores is not None else _scores_from_game(game)
        ),
        narrator_intro=narrator_intro,
    )


@router.get("/content", response_model=ContentOut)
async def get_content(locale: str | None = None):
    return ContentOut(**content_bundle(locale))


@router.post("/games", response_model=GameOut)
async def create_game(
    body: CreateGameRequest | None = None,
    games: GameService = Depends(get_game_service),
):
    seats = None
    locale = None
    if body:
        locale = body.locale
        if body.seats:
            seats = [
                SeatConfig(
                    role=SeatRole(s.role),
                    player_type=PlayerType(s.player_type),
                    model=s.model,
                    temperature=s.temperature,
                    display_name=s.display_name,
                )
                for s in body.seats
            ]
    game = await games.create_game(seats)
    return _game_out(game, locale=locale)


@router.get("/games/{game_id}", response_model=GameOut)
async def get_game(game_id: str, games: GameService = Depends(get_game_service)):
    game = await games.get_game(game_id)
    return _game_out(game)


@router.post("/games/{game_id}/turns/{turn_number}/moves", response_model=MoveOut)
async def submit_move(
    game_id: str,
    turn_number: int,
    body: SubmitMoveRequest,
    turns: TurnService = Depends(get_turn_service),
):
    move = await turns.submit_human_move(game_id, turn_number, body.move_text)
    return MoveOut(
        seat_role=move.seat_role.value,  # type: ignore[arg-type]
        move_text=move.move_text,
        turn_number=move.turn_number,
    )


@router.post("/games/{game_id}/turns/{turn_number}/off", response_model=OffAskOut)
async def ask_off(
    game_id: str,
    turn_number: int,
    body: OffAskRequest,
    turns: TurnService = Depends(get_turn_service),
):
    exchange = await turns.ask_off(
        game_id, turn_number, body.move_text, locale=body.locale
    )
    return OffAskOut(
        turn_number=exchange.turn_number,
        seat_role=exchange.seat_role,  # type: ignore[arg-type]
        question=exchange.question,
        answer=exchange.answer,
    )


@router.post("/games/{game_id}/turns/{turn_number}/replay", response_model=ResolveOut)
async def replay_turn(
    game_id: str,
    turn_number: int,
    body: SubmitMoveRequest,
    turns: TurnService = Depends(get_turn_service),
):
    result = await turns.replay_turn(
        game_id, turn_number, body.move_text, locale=body.locale
    )
    data = await turns.get_turn(game_id, turn_number)
    return _resolve_out(result, turn_number, data)


@router.post("/games/{game_id}/turns/{turn_number}/resolve", response_model=ResolveOut)
async def resolve_turn(
    game_id: str,
    turn_number: int,
    turns: TurnService = Depends(get_turn_service),
    locale: str | None = None,
):
    result = await turns.resolve_turn(game_id, turn_number, locale=locale)
    data = await turns.get_turn(game_id, turn_number)
    return _resolve_out(result, turn_number, data)


@router.get("/games/{game_id}/turns/{turn_number}", response_model=TurnOut)
async def get_turn(
    game_id: str,
    turn_number: int,
    turns: TurnService = Depends(get_turn_service),
):
    data = await turns.get_turn(game_id, turn_number)
    adj = data["adjudication"]
    return TurnOut(
        turn_number=turn_number,
        moves=[
            MoveOut(
                seat_role=m.seat_role.value,  # type: ignore[arg-type]
                move_text=m.move_text,
                turn_number=m.turn_number,
            )
            for m in data["moves"]
        ],
        adjudication=(
            AdjudicationOut(
                turn_number=adj.turn_number,
                world_narrative=adj.world_narrative,
                world_state_digest=adj.world_state_digest or "",
                seat_feedback=adj.seat_feedback,
            )
            if adj
            else None
        ),
        scores=_scores_out(data["scores"]),
        deltas=data.get("deltas"),
    )


@router.get("/games/{game_id}/history", response_model=HistoryOut)
async def get_history(
    game_id: str,
    turns: TurnService = Depends(get_turn_service),
):
    history = await turns.get_history(game_id)
    return HistoryOut(
        game_id=game_id,
        history=[
            HistoryPointOut(
                turn_number=turn,
                scores=_scores_out(scores),  # type: ignore[arg-type]
            )
            for turn, scores in history
        ],
    )
