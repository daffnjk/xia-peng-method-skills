#!/usr/bin/env python3
"""Stage a course with preflight checks, exclusive locking and exception rollback.

This is not a crash-proof database transaction. SIGKILL/power loss can leave a
lock or an orphan intake; inspect it before manually recovering. Never auto-unlock.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

import yaml

from assetlib import AssetError, ROOT, digest, safe_path

ID_RE = re.compile(r'^XP-T-(\d{3,})$')
FIELDS = ['source_id', 'title', 'series', 'session', 'recording_date', 'publish_date',
          'speaker', 'source_type', 'raw_path', 'reviewed_path', 'has_timecodes',
          'rights_status', 'status', 'source_version', 'added_at', 'notes']
RIGHTS = ('not_recorded', 'internal_only', 'internal_only_pending_confirmation',
          'authorized', 'public_source')


def load_manifest(path: Path) -> tuple[list[str], list[dict], bytes | None]:
    if not path.exists():
        return FIELDS[:], [], None
    original = path.read_bytes()
    reader = csv.DictReader(io.StringIO(original.decode('utf-8-sig')))
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not set(FIELDS).issubset(fields):
        raise AssetError('Manifest needs unique columns including all documented fields')
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise AssetError('Manifest row width mismatch')
    ids = [r['source_id'] for r in rows]
    if len(ids) != len(set(ids)) or any(not ID_RE.fullmatch(s) for s in ids):
        raise AssetError('Manifest has duplicate/invalid source IDs')
    return fields, rows, original


def next_source_id(rows: list[dict], source_root: Path) -> str:
    numbers = [int(ID_RE.fullmatch(r['source_id'])[1]) for r in rows]
    for rel in ('inbox', 'raw', 'reviewed'):
        directory = source_root / rel
        if directory.exists():
            for entry in directory.iterdir():
                match = re.match(r'^XP-T-(\d{3,})(?:_|$)', entry.name)
                if match:
                    numbers.append(int(match[1]))
    return f'XP-T-{max(numbers, default=0) + 1:03d}'


def stage(root: Path, *, title: str, transcript: Path | None = None, source_id: str = '',
          series: str = '', session: str = '', date: str = '', speaker: str = '夏鹏',
          rights_status: str = 'not_recorded') -> tuple[str, Path]:
    root = root.absolute()
    if not root.is_dir() or root.is_symlink():
        raise AssetError('Root must be an existing, non-symlink repository directory')
    if not title.strip() or any('\x00' in s for s in (title, series, session, speaker)):
        raise AssetError('Title is required; NUL characters are not allowed')
    if rights_status not in RIGHTS:
        raise AssetError('Unknown rights status')
    if date:
        if dt.date.fromisoformat(date).isoformat() != date:
            raise AssetError('Recording date must be YYYY-MM-DD')
    if source_id and not ID_RE.fullmatch(source_id):
        raise AssetError('Invalid source ID')
    transcript_bytes = None
    suffix = '.txt'
    if transcript is not None:
        transcript = transcript.expanduser().absolute()
        if transcript.is_symlink() or not transcript.is_file():
            raise AssetError('Transcript must be an existing regular file, not a symlink')
        if transcript.suffix.lower() not in ('.txt', '.md'):
            raise AssetError('Provide a UTF-8 .txt/.md transcript; extract binary documents first')
        transcript_bytes = transcript.read_bytes()
        if not transcript_bytes.strip():
            raise AssetError('Transcript is empty')
        transcript_bytes.decode('utf-8-sig')
        suffix = transcript.suffix.lower()
    manifest = safe_path(root, '01_source/manifest.csv')
    source_root = safe_path(root, '01_source')
    inbox = safe_path(root, '01_source/inbox')
    # Validate the existing state before any side effects.
    load_manifest(manifest)
    source_root.mkdir(exist_ok=True)
    lock = safe_path(root, '01_source/.ingestion.lock')
    try:
        lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise AssetError('Ingestion lock exists; another writer or recovery is pending') from exc
    temp_dir: Path | None = None
    temp_manifest: Path | None = None
    intake: Path | None = None
    installed = False
    original: bytes | None = None
    new_bytes = b''
    try:
        with os.fdopen(lock_fd, 'w', encoding='utf-8') as handle:
            json.dump({'pid': os.getpid(), 'operation': 'course intake'}, handle)
        fields, rows, original = load_manifest(manifest)  # recheck inside the lock
        sid = source_id or next_source_id(rows, source_root)
        if any(row['source_id'] == sid for row in rows):
            raise AssetError(f'Source ID already registered: {sid}')
        intake = safe_path(root, '01_source/inbox/' + sid)
        if intake.exists():
            raise AssetError(f'Intake already exists: {sid}; review it instead of overwriting')
        for rel in ('raw', 'reviewed'):
            directory = safe_path(root, '01_source/' + rel)
            if directory.exists() and any(directory.glob(sid + '_*')):
                raise AssetError(f'Source assets already exist for {sid}')
        if transcript_bytes is not None:
            for row in rows:
                if row['raw_path']:
                    existing = safe_path(root, row['raw_path'])
                    if existing.is_file() and digest(existing.read_bytes()) == digest(transcript_bytes):
                        raise AssetError(f'Transcript already registered as {row["source_id"]}')
        inbox.mkdir(exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(prefix='.intake-', dir=source_root))
        raw_rel = f'01_source/inbox/{sid}/raw_transcript{suffix}' if transcript_bytes is not None else ''
        metadata = {
            'course': {'source_id': sid, 'title': title, 'series': series, 'session': session,
                       'recording_date': date or None, 'publish_date': None, 'speaker': speaker,
                       'source_type': 'transcript', 'original_filename': transcript.name if transcript else '',
                       'language': 'zh-CN'},
            'source_quality': {'has_audio_or_video': False, 'has_timecodes': False,
                               'has_speaker_labels': False, 'has_slides_or_handout': False,
                               'transcription_method': 'unknown', 'known_typos_or_terms': []},
            'rights': {'status': rights_status, 'notes': ''},
            'integration_goal': {'priority': 'normal', 'expected_domain': '', 'expected_skill': '',
                                 'use_for_public_product': False, 'notes': ''},
            'processing': {'status': 'received', 'reviewer': '', 'source_version': '1.0'},
        }
        (temp_dir / 'metadata.yaml').write_text(yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False), encoding='utf-8')
        if transcript_bytes is not None:
            (temp_dir / f'raw_transcript{suffix}').write_bytes(transcript_bytes)
        (temp_dir / 'correction_candidates.csv').write_text('original,normalized,confidence,occurrences,note\n', encoding='utf-8')
        (temp_dir / 'extraction_notes.md').write_text(f'# {sid} 提取候选\n\n待审核；不得直接进入运行知识库。\n', encoding='utf-8')
        row = dict.fromkeys(fields, '')
        row.update(source_id=sid, title=title, series=series, session=session, recording_date=date,
                   speaker=speaker, source_type='transcript', raw_path=raw_rel, reviewed_path='',
                   has_timecodes='false', rights_status=rights_status, status='received',
                   source_version='1.0', added_at=dt.date.today().isoformat())
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader(); writer.writerows(rows + [row])
        new_bytes = stream.getvalue().encode('utf-8-sig')
        fd, name = tempfile.mkstemp(prefix='.manifest-', dir=source_root)
        temp_manifest = Path(name)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(new_bytes); handle.flush(); os.fsync(handle.fileno())
        if (manifest.read_bytes() if manifest.exists() else None) != original:
            raise AssetError('Manifest changed outside the ingestion lock; refusing to overwrite')
        temp_dir.rename(intake); installed = True
        os.replace(temp_manifest, manifest)
        return sid, intake
    except BaseException:
        # Ordinary exceptions/interrupts roll back our own folder. A successful atomic
        # manifest replace is the commit point and is not rolled back by later cleanup.
        committed = bool(new_bytes) and manifest.exists() and manifest.read_bytes() == new_bytes
        if installed and intake is not None and intake.exists() and not committed:
            shutil.rmtree(intake)
        raise
    finally:
        if temp_dir is not None and temp_dir.exists():
            shutil.rmtree(temp_dir)
        if temp_manifest is not None and temp_manifest.exists():
            temp_manifest.unlink()
        lock.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--title', required=True)
    parser.add_argument('--transcript', type=Path)
    parser.add_argument('--source-id', default='')
    parser.add_argument('--series', default=''); parser.add_argument('--session', default='')
    parser.add_argument('--date', default=''); parser.add_argument('--speaker', default='夏鹏')
    parser.add_argument('--rights-status', choices=RIGHTS, default='not_recorded')
    args = vars(parser.parse_args())
    try:
        sid, intake = stage(**args)
        print(sid); print(intake)
        return 0
    except (AssetError, OSError, ValueError, UnicodeError) as exc:
        print(f'FAIL: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
