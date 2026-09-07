#!/usr/bin/env python3
"""Safely copy compatibility skill files into Codex's runtime directory.

Existing different files require --force. Target-only resources and skills are
never removed. --check and --dry-run do not write anything.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import tempfile


def validate_path(root: Path, path: Path, *, directory: bool = False) -> None:
    """Reject symlinks and file/directory collisions before any writes."""
    current = root
    parts = path.relative_to(root).parts
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlink is not supported: {current}")
        if not current.exists():
            continue
        needs_directory = directory or index < len(parts) - 1
        if needs_directory and not current.is_dir():
            raise ValueError(f"Expected directory: {current}")
        if not needs_directory and not current.is_file():
            raise ValueError(f"Expected regular file: {current}")


def plan_sync(root: Path) -> list[tuple[Path, Path, str]]:
    source_root = root / "04_skills"
    target_root = root / ".agents" / "skills"
    validate_path(root, source_root, directory=True)
    validate_path(root, target_root, directory=True)
    if not source_root.is_dir():
        raise ValueError(f"Missing source skills directory: {source_root}")

    plan = []
    skill_count = 0
    for skill_dir in sorted(source_root.iterdir()):
        if skill_dir.is_symlink():
            raise ValueError(f"Symlink is not supported: {skill_dir}")
        if not skill_dir.is_dir():
            continue
        entry = skill_dir / "SKILL.md"
        validate_path(root, entry)
        if not entry.is_file():
            continue
        skill_count += 1
        for source in sorted(skill_dir.rglob("*")):
            if source.is_symlink():
                raise ValueError(f"Symlink is not supported: {source}")
            target = target_root / source.relative_to(source_root)
            if source.is_dir():
                validate_path(root, target, directory=True)
                continue
            validate_path(root, source)
            validate_path(root, target)
            status = "new" if not target.exists() else (
                "same" if source.read_bytes() == target.read_bytes() else "changed"
            )
            plan.append((source, target, status))
    if not skill_count:
        raise ValueError(f"No skills containing SKILL.md found: {source_root}")
    return plan


def copy_atomic(source: Path, target: Path) -> None:
    """Replace one file without truncating an existing file on copy failure."""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".skill-sync-", dir=target.parent)
    os.close(fd)
    temporary_path = Path(temporary)
    try:
        shutil.copy2(source, temporary_path)
        os.replace(temporary_path, target)
    finally:
        temporary_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Exit 1 on missing/different source-owned files; do not write")
    mode.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    mode.add_argument("--force", action="store_true", help="Explicitly allow replacing different existing files")
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()

    try:
        plan = plan_sync(root)
        changes = [(source, target, status) for source, target, status in plan if status != "same"]
        for _, target, status in changes:
            print(f"{status}: {target.relative_to(root).as_posix()}")
        if args.check:
            print("FAIL: source-owned files are out of sync" if changes else "PASS: source-owned files are in sync")
            return int(bool(changes))
        if args.dry_run:
            print(f"DRY RUN: {len(changes)} file(s); no files written")
            return 0
        if any(status == "changed" for _, _, status in changes) and not args.force:
            print("FAIL: existing files differ; review the diff and rerun with --force. No files written.")
            return 1
        for source, target, _ in changes:
            copy_atomic(source, target)
        print(f"Synced {len(changes)} file(s); target-only files and skills preserved")
        return 0
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
