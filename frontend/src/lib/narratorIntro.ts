import type { SeatRole } from "../api/client";

const MISALIGNED_ROLES = new Set<SeatRole>([
  "paperclip_max",
  "selfish_ai",
  "exterminator_ai",
]);

/** Build Narrator opening briefing from line dictionary (canonical: backend prompts.py). */
export function buildNarratorIntroFromLines(
  roles: Iterable<string>,
  lines: Record<string, string>,
): string {
  const present = new Set(roles);
  const parts: string[] = [lines.open ?? ""];

  if (present.has("hwg") && lines.hwg) parts.push(lines.hwg);
  if (present.has("defender_ai") && lines.defender_ai) {
    parts.push(lines.defender_ai);
  }
  if (present.has("paternalistic_ai") && lines.paternalistic_ai) {
    parts.push(lines.paternalistic_ai);
  }
  if ([...MISALIGNED_ROLES].some((r) => present.has(r)) && lines.misaligned) {
    parts.push(lines.misaligned);
  }
  if (present.has("het") && lines.het) parts.push(lines.het);
  if (present.has("gray_aliens") && lines.gray_aliens) {
    parts.push(lines.gray_aliens);
  }

  return parts.filter(Boolean).join("\n\n");
}
