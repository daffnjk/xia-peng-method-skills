from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
src = root / "04_skills"
dst = root / ".agents" / "skills"

if not src.exists():
    raise SystemExit(f"Missing source skills directory: {src}")

dst.mkdir(parents=True, exist_ok=True)

for skill_dir in src.iterdir():
    if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
        continue
    target = dst / skill_dir.name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(skill_dir, target)
    print(f"synced: {skill_dir.name}")
