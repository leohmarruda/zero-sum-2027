"""HTTP routes — game lifecycle and turns (spec.md §2.11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_game_service, get_turn_service
from app.api.schemas import (
    AdjudicationOut,
    CategoryScoresOut,
    CreateGameRequest,
    GameOut,
    HistoryOut,
    HistoryPointOut,
    MoveOut,
    ResolveOut,
    SeatOut,
    SubmitMoveRequest,
    TurnOut,
)
from app.domain.types import CategoryScores, TurnScores
from app.models import Game, GameStatus, PlayerType, SeatRole
from app.services.game_service import GameService, SeatConfig
from app.services.turn_service import TurnService

router = APIRouter()


def _scores_out(scores: TurnScores | None) -> dict[str, CategoryScoresOut] | None:
    if scores is None:
        return None
    return {role: CategoryScoresOut(**cats.as_dict()) for role, cats in scores.items()}


def _scores_from_game(game: Game) -> TurnScores | None:
    by_turn: dict[int, TurnScores] = {}
    for row in game.scores:
        if row.seat_role.value not in ("rogue_ai", "defender_ai", "humanity"):
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
    scores = by_turn.get(turn)
    return scores if scores and len(scores) == 3 else None


def _game_out(game: Game, scores: TurnScores | None = None) -> GameOut:
    return GameOut(
        id=game.id,
        status=game.status.value,  # type: ignore[arg-type]
        current_turn=game.current_turn,
        turn_cap=game.turn_cap,
        humanity_win_turn=game.humanity_win_turn,
        winner=game.winner,
        ended_at=game.ended_at,
        seats=[
            SeatOut(
                role=s.role.value,  # type: ignore[arg-type]
                player_type=s.player_type.value,  # type: ignore[arg-type]
                model=s.model,
                temperature=s.temperature,
            )
            for s in sorted(game.seats, key=lambda s: s.role.value)
        ],
        current_scores=_scores_out(scores if scores is not None else _scores_from_game(game)),  # type: ignore[arg-type]
    )


@router.post("/games", response_model=GameOut)
async def create_game(
    body: CreateGameRequest | None = None,
    games: GameService = Depends(get_game_service),
):
    seats = None
    if body and body.seats:
        seats = [
            SeatConfig(
                role=SeatRole(s.role),
                player_type=PlayerType(s.player_type),
                model=s.model,
                temperature=s.temperature,
            )
            for s in body.seats
        ]
    game = await games.create_game(seats)
    return _game_out(game)


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


@router.post("/games/{game_id}/turns/{turn_number}/resolve", response_model=ResolveOut)
async def resolve_turn(
    game_id: str,
    turn_number: int,
    turns: TurnService = Depends(get_turn_service),
):
    result = await turns.resolve_turn(game_id, turn_number)
    data = await turns.get_turn(game_id, turn_number)
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
        adjudication=AdjudicationOut(
            turn_number=result.adjudication.turn_number,
            world_narrative=result.adjudication.world_narrative,
            seat_feedback=result.adjudication.seat_feedback,
        ),
        scores=_scores_out(result.scores),  # type: ignore[arg-type]
    )
    return ResolveOut(
        game=_game_out(result.game, result.scores),
        turn=turn_payload,
        already_resolved=result.already_resolved,
    )


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
                seat_feedback=adj.seat_feedback,
            )
            if adj
            else None
        ),
        scores=_scores_out(data["scores"]),  # type: ignore[arg-type]
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
