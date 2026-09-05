from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
errors = []

if not (root / "AGENTS.md").exists():
    errors.append("Missing AGENTS.md")

skills_root = root / ".agents" / "skills"
expected = {
    "xia-peng-method-router",
    "understand-me",
    "scene-skill-builder",
    "goal-management",
    "agent-team-workflow",
    "side-business-system",
}
found = set()

for p in skills_root.glob("*/SKILL.md"):
    text = p.read_text(encoding="utf-8")
    name = re.search(r"(?m)^name:\s*(.+)$", text)
    desc = re.search(r"(?m)^description:\s*(.+)$", text)
    if not name or not desc:
        errors.append(f"Missing name/description frontmatter: {p}")
    if name:
        found.add(name.group(1).strip())

missing = expected - found
if missing:
    errors.append("Missing expected skills: " + ", ".join(sorted(missing)))

for rel in [
    "02_knowledge/principle_cards.yaml",
    "02_knowledge/case_cards.yaml",
    "02_knowledge/claim_audit.yaml",
    "01_source/raw/XP-T-001_raw.txt",
    "01_source/raw/XP-T-002_raw.txt",
    "01_source/raw/XP-T-003_raw.txt",
    "06_evals/evals.jsonl",
    "08_ops/INCREMENTAL_INGESTION_SOP.md",
]:
    if not (root / rel).exists():
        errors.append(f"Missing required asset: {rel}")

if errors:
    print("FAIL")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("PASS")
print(f"Codex project: {root}")
print(f"Skills detected: {len(found)}")
for name in sorted(found):
    print("-", name)
