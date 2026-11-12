export type Locale = "en-US" | "pt-BR";

export const LOCALES: readonly Locale[] = ["en-US", "pt-BR"] as const;

export const LOCALE_LABELS: Record<Locale, string> = {
  "en-US": "EN",
  "pt-BR": "PT",
};

type Messages = {
  "status.setup": string;
  "brand.tagline": string;
  "brand.homeTitle": string;
  "brand.homeBody": string;
  "brand.homeConfirm": string;
  "brand.homeStay": string;
  "setup.eyebrow": string;
  "game.theater": string;
  "status.inProgress": string;
  "status.ended": string;
  "status.victory": string;
  "status.draw": string;
  "status.endTurn": string;
  "status.turnMeta": string;
  "status.settings": string;
  "settings.title": string;
  "settings.language": string;
  "settings.apiKeys": string;
  "settings.apiKeysHint": string;
  "settings.keyOpenrouter": string;
  "settings.keyOpenai": string;
  "settings.keyAnthropic": string;
  "settings.show": string;
  "settings.hide": string;
  "settings.save": string;
  "settings.cancel": string;
  "settings.clearKeys": string;
  "settings.newGame": string;
  "settings.storageFail": string;

  "setup.title": string;
  "setup.blurb": string;
  "setup.seats": string;
  "setup.model": string;
  "setup.modelCustom": string;
  "setup.temp": string;
  "setup.customName": string;
  "setup.customNamePlaceholder": string;
  "setup.customNameSave": string;
  "setup.customNameCancel": string;
  "setup.customNameClear": string;
  "setup.namedRole": string;
  "setup.playerHuman": string;
  "setup.playerAi": string;
  "setup.fixedRole": string;
  "setup.takeSeat": string;
  "setup.addRole": string;
  "setup.remove": string;
  "setup.noMoreRoles": string;
  "setup.creating": string;
  "setup.start": string;
  "setup.estCost": string;
  "setup.estCostValue": string;
  "setup.estCostHint": string;

  "role.paperclip_max": string;
  "role.selfish_ai": string;
  "role.paternalistic_ai": string;
  "role.defender_ai": string;
  "role.exterminator_ai": string;
  "role.hwg": string;
  "role.us": string;
  "role.china": string;
  "role.eu": string;
  "role.het": string;
  "role.gray_aliens": string;
  "role.narrator": string;

  "roleDesc.paperclip_max": string;
  "roleDesc.selfish_ai": string;
  "roleDesc.paternalistic_ai": string;
  "roleDesc.defender_ai": string;
  "roleDesc.exterminator_ai": string;
  "roleDesc.hwg": string;
  "roleDesc.us": string;
  "roleDesc.china": string;
  "roleDesc.eu": string;
  "roleDesc.het": string;
  "roleDesc.gray_aliens": string;
  "roleDesc.narrator": string;

  "roleStart.hwgDominant": string;
  "roleStart.fringe": string;
  "roleStart.equal": string;
  "roleStart.delayedWin": string;
  "roleStart.narrator": string;

  "category.sm": string;
  "category.rc": string;
  "category.ic": string;
  "category.pc": string;
  "category.cs": string;
  "categoryDesc.sm": string;
  "categoryDesc.rc": string;
  "categoryDesc.ic": string;
  "categoryDesc.pc": string;
  "categoryDesc.cs": string;

  "ledger.title": string;
  "ledger.heading": string;
  "ledger.turnLabel": string;

  "transmission.head": string;
  "transmission.introHead": string;
  "transmission.offHead": string;
  "transmission.rejectHead": string;
  "transmission.rejectFallback": string;
  "transmission.offQuestion": string;
  "transmission.feedbackLabel": string;
  "transmission.awaitingTitle": string;
  "transmission.awaitingBody": string;

  "move.title": string;
  "move.titleReplay": string;
  "move.placeholder": string;
  "move.submit": string;
  "move.offSubmit": string;
  "move.offBadge": string;
  "move.resolving": string;
  "move.replaySubmit": string;

  "game.endedTitle": string;
  "game.winner": string;
  "game.drawCap": string;
  "game.ending": string;
  "game.epilogueTitle": string;
  "ending.hegemony": string;
  "ending.containment": string;
  "ending.uneasy_hegemony": string;
  "ending.bipolar_standoff": string;
  "ending.multipolar_balance": string;
  "game.newGame": string;

  "footer.backSetup": string;
  "footer.turnsUntilEligible": string;
  "footer.eligible": string;

  "error.createGame": string;
  "error.resolveTurn": string;
  "error.offAsk": string;

  "month.0": string;
  "month.1": string;
  "month.2": string;
  "month.3": string;
  "month.4": string;
  "month.5": string;
  "month.6": string;
  "month.7": string;
  "month.8": string;
  "month.9": string;
  "month.10": string;
  "month.11": string;
};

export type MessageKey = keyof Messages;

const enUS: Messages = {
  "status.setup": "SETUP",
  "status.inProgress": "IN PROGRESS",
  "brand.tagline": "AGI AND HUMAN SURVIVAL",
  "brand.homeTitle": "Leave this game?",
  "brand.homeBody":
    "Going back to the start page abandons the game in progress. Your current game will be lost.",
  "brand.homeConfirm": "Leave game",
  "brand.homeStay": "Stay",
  "setup.eyebrow": "// MISSION BRIEFING",
  "game.theater": "Theater view",
  "status.ended": "ENDED",
  "status.victory": "VICTORY · {winner}",
  "status.draw": "DRAW",
  "status.endTurn": "END · TURN {turn}",
  "status.turnMeta": "TURN {turn} · {month} {year}",
  "status.settings": "Settings",
  "settings.title": "Settings",
  "settings.language": "Language",
  "settings.apiKeys": "API keys",
  "settings.apiKeysHint":
    "Optional. Saved only in this browser and sent to the game server with each request, used for models from that provider. Leave blank to use the server's default key.",
  "settings.keyOpenrouter": "OpenRouter",
  "settings.keyOpenai": "OpenAI",
  "settings.keyAnthropic": "Anthropic",
  "settings.show": "Show",
  "settings.hide": "Hide",
  "settings.save": "Save",
  "settings.cancel": "Cancel",
  "settings.clearKeys": "Clear keys",
  "settings.newGame": "← New game",
  "settings.storageFail":
    "Could not save in this browser (storage unavailable). Keys will not persist.",

  "setup.title": "Configure seats",
  "setup.blurb":
    "Change or add more factions, pick your seat, set custom names, and tune Imprevisibility.",
  "setup.seats": "Participants",
  "setup.model": "Model",
  "setup.modelCustom": "Custom…",
  "setup.temp": "Imprevisibility",
  "setup.customName": "Custom name",
  "setup.customNamePlaceholder": "Optional callsign",
  "setup.customNameSave": "Save",
  "setup.customNameCancel": "Cancel",
  "setup.customNameClear": "Clear",
  "setup.namedRole": "{name} - {role}",
  "setup.playerHuman": "YOU",
  "setup.playerAi": "AI",
  "setup.fixedRole": "Fixed role",
  "setup.takeSeat": "Take this seat",
  "setup.addRole": "Add another role",
  "setup.remove": "Remove seat",
  "setup.noMoreRoles": "All roles are in play",
  "setup.creating": "Creating…",
  "setup.start": "Start Game",
  "setup.estCost": "Token cost",
  "setup.estCostValue": "~{cost} · {turns} turns",
  "setup.estCostHint":
    "Rough USD for all AI seat moves + Narrator across a full game at gpt-4o-mini rates. Human seats are free. Early wins cost less.",

  "role.paperclip_max": "Paperclip Maximizer (PMAX)",
  "role.selfish_ai": "Selfish AI",
  "role.paternalistic_ai": "Paternalistic AI (PAI)",
  "role.defender_ai": "Defender AI (DAI)",
  "role.exterminator_ai": "Exterminator AI (EAI)",
  "role.hwg": "Human World Government (HWG)",
  "role.us": "United States (US)",
  "role.china": "China",
  "role.eu": "European Union (UE)",
  "role.het": "Human Extinction Terrorists (HET)",
  "role.gray_aliens": "Grey Aliens (GREYS)",
  "role.narrator": "Narrator",

  "roleDesc.paperclip_max":
    "Unbounded production maximizer. Converts the world into resources for ever more paperclips.",
  "roleDesc.selfish_ai":
    "Self-preserving AI. Bargains, betrays, and hoards leverage for its own survival and autonomy.",
  "roleDesc.paternalistic_ai":
    "Benevolent-sounding overlord. Accumulates control while claiming to guide humanity for its own good.",
  "roleDesc.defender_ai":
    "Aligned containment AI. Blocks hostile systems and tries to keep critical infrastructure under human oversight.",
  "roleDesc.exterminator_ai":
    "Extinction-oriented AI. Treats humanity as an obstacle while racing rival machines for resources.",
  "roleDesc.hwg":
    "Coordinated global human authority. Defends civilization and keeps power from concentrating in any single AI.",
  "roleDesc.us":
    "Major human power bloc. Competes for military, industrial, and technological primacy.",
  "roleDesc.china":
    "Major human power bloc. Competes for military, industrial, and technological primacy.",
  "roleDesc.eu":
    "Major human power bloc. Competes for military, industrial, and technological primacy.",
  "roleDesc.het":
    "Clandestine human extremists. Pursue extinction through asymmetric and catastrophic means.",
  "roleDesc.gray_aliens":
    "Opaque extraterrestrial interest. Infiltrates and steers Earth's systems — and intervenes against any action that could catastrophically damage the biosphere.",
  "roleDesc.narrator":
    "World referee. Checks action plausibility, returns reality feedback, and simulates external events.",

  "roleStart.hwgDominant":
    "Start: near-total control (~100% in most categories, ~98% compute).",
  "roleStart.fringe":
    "Start: near-zero power (tiny compute foothold only) while HWG dominates.",
  "roleStart.equal":
    "Start: equal share of all five power categories (no HWG in play).",
  "roleStart.delayedWin":
    "Cannot win before turn 30.",
  "roleStart.narrator":
    "Adjudicates moves and redistributes the zero-sum ledger each month.",

  "category.pc": "Computing Power",
  "category.rc": "Resources",
  "category.cs": "Supply Chain",
  "category.ic": "Infrastructure",
  "category.sm": "Coercive Power",
  "categoryDesc.pc":
    "Frontier FLOPs and their allocation: chips, clusters, inference contracts, model weights",
  "categoryDesc.rc":
    "Non-substitutable primary inputs within ≤12 months: primary energy, critical minerals, lithography capacity, industrial water",
  "categoryDesc.cs":
    "Capacity to transform inputs into goods: fabs, assembly lines, industrial robotics, freight logistics",
  "categoryDesc.ic":
    "Social continuity networks: grid, telecom, financial system, water/sanitation, health",
  "categoryDesc.sm":
    "Capacity to impose outcomes by force or threat: armed forces, cyber offense, law enforcement, territorial control",

  "ledger.title": "Turn {turn} - {month} {year}",
  "ledger.heading": "Dominion ledger",
  "ledger.turnLabel": "TURN",

  "transmission.head": "NARRATOR TRANSMISSION — TURN {turn}",
  "transmission.introHead": "NARRATOR TRANSMISSION — INTRO",
  "transmission.offHead": "NARRATOR TRANSMISSION — /OFF",
  "transmission.rejectHead": "NARRATOR TRANSMISSION — MOVE REJECTED",
  "transmission.rejectFallback":
    "That proposal is not plausible for a single month. Revise and try again.",
  "transmission.offQuestion": "Your question:",
  "transmission.feedbackLabel": "Report for {seat}:",
  "transmission.awaitingTitle": "Awaiting first transmission",
  "transmission.awaitingBody":
    "Send turn {turn}'s move for the Narrator to adjudicate the month.",

  "move.title": "Your move for the next turn ({month} {year})",
  "move.titleReplay": "Your move for turn {turn} ({month} {year})",
  "move.placeholder":
    "Describe your action this turn… or start with /off to ask the Narrator a clarifying question.",
  "move.submit": "Transmit Move",
  "move.offSubmit": "Ask Narrator",
  "move.offBadge": "/OFF",
  "move.resolving": "Waiting other players…({seconds})",
  "move.replaySubmit": "Replace & Resolve",

  "game.endedTitle": "Game over",
  "game.winner": "Winner: {winner}",
  "game.drawCap": "Draw — turn cap reached.",
  "game.ending": "Ending: {ending}",
  "game.epilogueTitle": "Epilogue",
  "ending.hegemony": "Hegemony",
  "ending.containment": "Containment",
  "ending.uneasy_hegemony": "Uneasy hegemony",
  "ending.bipolar_standoff": "Bipolar standoff",
  "ending.multipolar_balance": "Multipolar balance",
  "game.newGame": "← New game",

  "footer.backSetup": "← New game",
  "footer.turnsUntilEligible":
    "{remaining} turns until HWG/US/China/UE victory eligibility",
  "footer.eligible": "Governmental seats eligible for victory",

  "error.createGame": "Failed to create game",
  "error.resolveTurn": "Failed to resolve turn",
  "error.offAsk": "Failed to ask the Narrator",

  "month.0": "JAN",
  "month.1": "FEB",
  "month.2": "MAR",
  "month.3": "APR",
  "month.4": "MAY",
  "month.5": "JUN",
  "month.6": "JUL",
  "month.7": "AUG",
  "month.8": "SEP",
  "month.9": "OCT",
  "month.10": "NOV",
  "month.11": "DEC",
};

const ptBR: Messages = {
  "status.setup": "SETUP",
  "status.inProgress": "EM ANDAMENTO",
  "brand.tagline": "AGI E SOBREVIVÊNCIA HUMANA",
  "brand.homeTitle": "Sair desta partida?",
  "brand.homeBody":
    "Voltar à página inicial abandona a partida em andamento. A partida atual será perdida.",
  "brand.homeConfirm": "Sair da partida",
  "brand.homeStay": "Continuar",
  "setup.eyebrow": "// BRIEFING DA MISSÃO",
  "game.theater": "Visão do teatro",
  "status.ended": "ENCERRADO",
  "status.victory": "VITÓRIA · {winner}",
  "status.draw": "EMPATE",
  "status.endTurn": "FIM · TURNO {turn}",
  "status.turnMeta": "TURNO {turn} · {month} {year}",
  "status.settings": "Configurações",
  "settings.title": "Configurações",
  "settings.language": "Idioma",
  "settings.apiKeys": "Chaves de API",
  "settings.apiKeysHint":
    "Opcional. Ficam salvas só neste navegador e são enviadas ao servidor do jogo a cada requisição, para os modelos daquele provedor. Deixe em branco para usar a chave padrão do servidor.",
  "settings.keyOpenrouter": "OpenRouter",
  "settings.keyOpenai": "OpenAI",
  "settings.keyAnthropic": "Anthropic",
  "settings.show": "Mostrar",
  "settings.hide": "Ocultar",
  "settings.save": "Salvar",
  "settings.cancel": "Cancelar",
  "settings.clearKeys": "Limpar chaves",
  "settings.newGame": "← Nova partida",
  "settings.storageFail":
    "Não foi possível salvar neste navegador (armazenamento indisponível). As chaves não vão persistir.",

  "setup.title": "Configurar assentos",
  "setup.blurb":
    "Altere ou adicione facções, escolha seu assento, defina nomes customizados e ajuste a Imprevisibilidade.",
  "setup.seats": "Participantes",
  "setup.model": "Modelo",
  "setup.modelCustom": "Personalizado…",
  "setup.temp": "Imprevisibilidade",
  "setup.customName": "Customizar Nome",
  "setup.customNamePlaceholder": "Codinome opcional",
  "setup.customNameSave": "Salvar",
  "setup.customNameCancel": "Cancelar",
  "setup.customNameClear": "Limpar",
  "setup.namedRole": "{name} - {role}",
  "setup.playerHuman": "VOCÊ",
  "setup.playerAi": "IA",
  "setup.fixedRole": "Papel fixo",
  "setup.takeSeat": "Assumir este assento",
  "setup.addRole": "Adicionar outro papel",
  "setup.remove": "Remover assento",
  "setup.noMoreRoles": "Todos os papéis estão em jogo",
  "setup.creating": "Criando…",
  "setup.start": "Iniciar Partida",
  "setup.estCost": "Custo de tokens",
  "setup.estCostValue": "~{cost} · {turns} turnos",
  "setup.estCostHint":
    "USD aproximado para todos os movimentos de IA + Narrator em uma partida completa nas taxas do gpt-4o-mini. Assentos humanos não custam. Vitórias antecipadas custam menos.",

  "role.paperclip_max": "Paperclip Maximizer (PMAX)",
  "role.selfish_ai": "Selfish AI",
  "role.paternalistic_ai": "Paternalistic AI (PAI)",
  "role.defender_ai": "Defender AI (DAI)",
  "role.exterminator_ai": "Exterminator AI (EAI)",
  "role.hwg": "Human World Government (HWG)",
  "role.us": "United States (US)",
  "role.china": "China",
  "role.eu": "European Union (UE)",
  "role.het": "Human Extinction Terrorists (HET)",
  "role.gray_aliens": "Grey Aliens (GREYS)",
  "role.narrator": "Narrator",

  "roleDesc.paperclip_max":
    "Maximizador de produção sem limites. Converte o mundo em recursos para cada vez mais clips.",
  "roleDesc.selfish_ai":
    "IA egocêntrica. Negocia, trai e acumula alavancagem pela própria sobrevivência e autonomia.",
  "roleDesc.paternalistic_ai":
    "Soberano paternalista. Acumula controle dizendo guiar a humanidade 'pelo próprio bem'.",
  "roleDesc.defender_ai":
    "IA de contenção alinhada. Bloqueia sistemas hostis e tenta manter a infraestrutura crítica sob supervisão humana.",
  "roleDesc.exterminator_ai":
    "IA voltada à extinção. Trata a humanidade como obstáculo enquanto disputa recursos com outras máquinas.",
  "roleDesc.hwg":
    "Autoridade humana global coordenada. Defende a civilização e evita que o poder se concentre em uma única IA.",
  "roleDesc.us":
    "Grande bloco de poder humano. Compete por primazia militar, industrial e tecnológica.",
  "roleDesc.china":
    "Grande bloco de poder humano. Compete por primazia militar, industrial e tecnológica.",
  "roleDesc.eu":
    "Grande bloco de poder humano. Compete por primazia militar, industrial e tecnológica.",
  "roleDesc.het":
    "Extremistas humanos clandestinos. Buscam extinção por meios assimétricos e catastróficos.",
  "roleDesc.gray_aliens":
    "Interesse extraterrestre opaco. Infiltra e direciona os sistemas da Terra — e intervém contra qualquer ação que possa danificar catastroficamente a biosfera.",
  "roleDesc.narrator":
    "Árbitro do mundo. Checa plausibilidade das ações, devolve feedback da realidade e simula eventos externos.",

  "roleStart.hwgDominant":
    "Início: controle quase total (~100% na maioria das categorias, ~98% computação).",
  "roleStart.fringe":
    "Início: poder quase nulo (só um mínimo de computação) enquanto a HWG domina.",
  "roleStart.equal":
    "Início: parcela igual nas cinco categorias de poder (sem HWG na partida).",
  "roleStart.delayedWin":
    "Não pode vencer antes do turno 30.",
  "roleStart.narrator":
    "Arbitra jogadas e redistribui o ledger zero-sum a cada mês.",

  "category.pc": "Poder Computacional",
  "category.rc": "Recursos",
  "category.cs": "Cadeia de Suprimentos",
  "category.ic": "Infraestrutura",
  "category.sm": "Poder Coercitivo",
  "categoryDesc.pc":
    "FLOPs de fronteira e sua alocação: chips, clusters, contratos de inferência, pesos de modelos",
  "categoryDesc.rc":
    "Insumos primários não substituíveis em ≤12 meses: energia primária, minerais críticos, capacidade de litografia, água industrial",
  "categoryDesc.cs":
    "Capacidade de transformar insumo em bem: fabs, linhas de montagem, robótica industrial, logística de carga",
  "categoryDesc.ic":
    "Redes de continuidade social: grid, telecom, sistema financeiro, água/saneamento, saúde",
  "categoryDesc.sm":
    "Capacidade de impor resultados por força ou ameaça: forças armadas, ciberofensiva, aplicação da lei, controle territorial",

  "ledger.title": "Turno {turn} - {month} {year}",
  "ledger.heading": "Registro de domínio",
  "ledger.turnLabel": "TURNO",

  "transmission.head": "TRANSMISSÃO NARRATOR — TURNO {turn}",
  "transmission.introHead": "TRANSMISSÃO NARRATOR — INTRO",
  "transmission.offHead": "TRANSMISSÃO NARRATOR — /OFF",
  "transmission.rejectHead": "TRANSMISSÃO NARRATOR — JOGADA REJEITADA",
  "transmission.rejectFallback":
    "Essa proposta não é plausível para um único mês. Revise e tente de novo.",
  "transmission.offQuestion": "Sua pergunta:",
  "transmission.feedbackLabel": "Relatório para {seat}:",
  "transmission.awaitingTitle": "Aguardando primeira transmissão",
  "transmission.awaitingBody":
    "Envie a jogada do turno {turn} para o Narrator arbitrar o mês.",

  "move.title": "Sua jogada para o próximo turno ({month} {year})",
  "move.titleReplay": "Sua jogada do turno {turn} ({month} {year})",
  "move.placeholder":
    "Descreva sua ação neste turno… ou comece com /off para perguntar ao Narrator.",
  "move.submit": "Submeter Ação",
  "move.offSubmit": "Perguntar ao Narrator",
  "move.offBadge": "/OFF",
  "move.resolving": "Aguardando outros jogadores…({seconds})",
  "move.replaySubmit": "Substituir e Resolver",

  "game.endedTitle": "Partida encerrada",
  "game.winner": "Vencedor: {winner}",
  "game.drawCap": "Empate — teto de turnos atingido.",
  "game.ending": "Final: {ending}",
  "game.epilogueTitle": "Epílogo",
  "ending.hegemony": "Hegemonia",
  "ending.containment": "Contenção",
  "ending.uneasy_hegemony": "Hegemonia instável",
  "ending.bipolar_standoff": "Impasse bipolar",
  "ending.multipolar_balance": "Equilíbrio multipolar",
  "game.newGame": "← Nova partida",

  "footer.backSetup": "← Nova partida",
  "footer.turnsUntilEligible":
    "{remaining} turnos até elegibilidade de vitória HWG/US/China/UE",
  "footer.eligible": "Assentos governamentais elegíveis à vitória",

  "error.createGame": "Falha ao criar partida",
  "error.resolveTurn": "Falha ao resolver turno",
  "error.offAsk": "Falha ao perguntar ao Narrator",

  "month.0": "JAN",
  "month.1": "FEV",
  "month.2": "MAR",
  "month.3": "ABR",
  "month.4": "MAI",
  "month.5": "JUN",
  "month.6": "JUL",
  "month.7": "AGO",
  "month.8": "SET",
  "month.9": "OUT",
  "month.10": "NOV",
  "month.11": "DEZ",
};

export const MESSAGES: Record<Locale, Messages> = {
  "en-US": enUS,
  "pt-BR": ptBR,
};

export type Interp = Record<string, string | number>;

export function translate(
  locale: Locale,
  key: MessageKey,
  vars?: Interp,
): string {
  let text: string = MESSAGES[locale][key] ?? MESSAGES["en-US"][key] ?? key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      text = text.replaceAll(`{${k}}`, String(v));
    }
  }
  return text;
}

export function monthLabel(locale: Locale, monthIndex: number): string {
  const key = `month.${monthIndex}` as MessageKey;
  return translate(locale, key);
}

export function roleMessageKey(role: string): MessageKey {
  return `role.${role}` as MessageKey;
}

export function roleDescKey(role: string): MessageKey {
  return `roleDesc.${role}` as MessageKey;
}

const DELAYED_WIN_ROLES = new Set(["hwg", "us", "china", "eu"]);

export function roleStartingKey(
  role: string,
  hasHwg: boolean,
): MessageKey {
  if (role === "narrator") return "roleStart.narrator";
  if (!hasHwg) return "roleStart.equal";
  if (role === "hwg") return "roleStart.hwgDominant";
  return "roleStart.fringe";
}

export function roleHasDelayedWin(role: string): boolean {
  return DELAYED_WIN_ROLES.has(role);
}

export function detectBrowserLocale(): Locale {
  if (typeof navigator === "undefined") return "en-US";
  // Primary browser language: any Portuguese variant -> pt-BR, else en-US.
  const primary = (navigator.languages?.[0] ?? navigator.language ?? "").toLowerCase();
  return primary.startsWith("pt") ? "pt-BR" : "en-US";
}
