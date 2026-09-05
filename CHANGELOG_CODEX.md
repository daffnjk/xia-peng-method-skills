# v0.2.0 Codex Adapter

- Added repository-native `.agents/skills/career-planning` and routed career/life-planning requests to it.
- Extended `AGENTS.md` and `SYSTEM_PROMPT.md` to the fourth source, `XP-T-004`.
- Added stable paragraph anchors for the reviewed `XP-T-004` transcript; the earlier raw transcripts remain unanchored.
- Added career-planning regression coverage and current-data verification guardrails.

# v0.1.2 Codex Adapter

- Added root `AGENTS.md` for automatic Codex project instructions.
- Added repository-native `.agents/skills/` with six skills.
- Added private user context directory and Git ignore protection.
- Added `README_CODEX.md` with Desktop/CLI usage examples.
- Added skill sync and setup verification scripts.
- Corrected source citation policy: raw transcripts currently do not contain stable paragraph anchors, so Codex must not invent `#Pxxx` anchors.
