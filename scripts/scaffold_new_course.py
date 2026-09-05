#!/usr/bin/env python3
"""Create an intake folder and append a source row to manifest.csv.

This script does not alter the production knowledge base. It only stages a new
course for review.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import shutil
from pathlib import Path

ID_RE = re.compile(r"^XP-T-(\d{3,})$")


def next_source_id(manifest: Path) -> str:
    max_id = 0
    if manifest.exists():
        with manifest.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                match = ID_RE.match((row.get("source_id") or "").strip())
                if match:
                    max_id = max(max_id, int(match.group(1)))
    return f"XP-T-{max_id + 1:03d}"


def yaml_quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage a new Xia Peng course source")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--title", required=True)
    parser.add_argument("--series", default="")
    parser.add_argument("--session", default="")
    parser.add_argument("--date", default="", help="Recording date in YYYY-MM-DD, if known")
    parser.add_argument("--speaker", default="夏鹏")
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--source-id", default="")
    parser.add_argument("--rights-status", default="not_recorded")
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = root / "01_source" / "manifest.csv"
    source_id = args.source_id.strip() or next_source_id(manifest)
    if not ID_RE.match(source_id):
        raise SystemExit(f"Invalid source ID: {source_id}")

    intake_dir = root / "01_source" / "inbox" / source_id
    if intake_dir.exists():
        raise SystemExit(f"Intake directory already exists: {intake_dir}")
    intake_dir.mkdir(parents=True)

    raw_rel = ""
    if args.transcript:
        transcript = args.transcript.expanduser().resolve()
        if not transcript.is_file():
            raise SystemExit(f"Transcript not found: {transcript}")
        suffix = transcript.suffix or ".txt"
        target = intake_dir / f"raw_transcript{suffix}"
        shutil.copy2(transcript, target)
        raw_rel = target.relative_to(root).as_posix()

    metadata = f"""course:\n  source_id: {yaml_quote(source_id)}\n  title: {yaml_quote(args.title)}\n  series: {yaml_quote(args.series)}\n  session: {yaml_quote(args.session)}\n  recording_date: {yaml_quote(args.date) if args.date else 'null'}\n  publish_date: null\n  speaker: {yaml_quote(args.speaker)}\n  source_type: transcript\n  original_filename: {yaml_quote(args.transcript.name) if args.transcript else '""'}\n  language: zh-CN\n\nsource_quality:\n  has_audio_or_video: false\n  has_timecodes: false\n  has_speaker_labels: false\n  has_slides_or_handout: false\n  transcription_method: unknown\n  known_typos_or_terms: []\n\nrights:\n  status: {yaml_quote(args.rights_status)}\n  notes: ""\n\nintegration_goal:\n  priority: normal\n  expected_domain: ""\n  expected_skill: ""\n  use_for_public_product: false\n  notes: ""\n\nprocessing:\n  status: received\n  reviewer: ""\n  source_version: "1.0"\n"""
    (intake_dir / "metadata.yaml").write_text(metadata, encoding="utf-8")
    (intake_dir / "correction_candidates.csv").write_text(
        "original,normalized,confidence,occurrences,note\n", encoding="utf-8-sig"
    )
    (intake_dir / "extraction_notes.md").write_text(
        f"# {source_id} 提取笔记\n\n## 课程主线\n\n## 原则候选\n\n## 模型候选\n\n## 案例候选\n\n## 冲突候选\n\n## 风险主张\n\n## Skill 候选\n",
        encoding="utf-8",
    )

    if not manifest.exists():
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            "source_id,title,series,session,recording_date,publish_date,speaker,source_type,raw_path,reviewed_path,has_timecodes,rights_status,status,source_version,added_at,notes\n",
            encoding="utf-8-sig",
        )

    row = {
        "source_id": source_id,
        "title": args.title,
        "series": args.series,
        "session": args.session,
        "recording_date": args.date,
        "publish_date": "",
        "speaker": args.speaker,
        "source_type": "transcript",
        "raw_path": raw_rel,
        "reviewed_path": "",
        "has_timecodes": "false",
        "rights_status": args.rights_status,
        "status": "received",
        "source_version": "1.0",
        "added_at": dt.date.today().isoformat(),
        "notes": "",
    }
    with manifest.open("r", encoding="utf-8-sig", newline="") as fh:
        fieldnames = csv.DictReader(fh).fieldnames
    if not fieldnames:
        raise SystemExit("Manifest has no header")
    with manifest.open("a", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writerow(row)

    print(source_id)
    print(intake_dir)


if __name__ == "__main__":
    main()
