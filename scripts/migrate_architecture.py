#!/usr/bin/env python3
"""One-time, auditable migration from reviewed PR #1 assets to schema 1.0.

Preserves source bytes and knowledge statements. Historic XP-T-001..003 anchors
are archived, not guessed. Run only in a disposable clean branch, then inspect diff.
"""
from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path
import re
import shutil

import yaml

from assetlib import (AssetError, DIMENSIONS, KINDS, PREFIXES, ROOT, blob_sha,
                      canonical, digest, frontmatter, jsonl, manifest_rows,
                      read_text, safe_path, yaml_load)

EXPECTED = {
    '02_knowledge/principle_cards.yaml': 'b3512e323e9e28bc4d3a746201985e495a834a5d',
    '02_knowledge/case_cards.yaml': '79de71445738daeb8c1da02405e7aaf272d37419',
    '02_knowledge/claim_audit.yaml': '19dfc525955bd5d6940befe7c34d09b7009383ab',
    '02_knowledge/contradictions.yaml': '44455812634193605479620818dd9a8de6c26d26',
    '02_knowledge/model_registry.yaml': '86a1422dcf887d23b199bc18604d703135076815',
    '06_evals/evals.jsonl': '08ceefdbf0e7c66a010968eaf3c4c15376bd3941',
    '01_source/raw/XP-T-001_raw.txt': 'd4fa82c00b7c68001088ed88f833a635029f9d03',
    '01_source/raw/XP-T-002_raw.txt': 'e5d38e96cc3daf37ce97c49c693daa43e08b174a',
    '01_source/raw/XP-T-003_raw.txt': '7ab8f3433fe24ba6661de8d743999f3d6df40f64',
    '01_source/raw/XP-T-004_raw.txt': 'd4255558b10e0046425686f32c6675f01ab0e3e7',
    '01_source/reviewed/XP-T-004_reviewed.txt': '75a617aa599b1e957e2d6a360fd169f76c7a3c36',
}
LEGACY = re.compile(r'^(XP-T-00[123])#P\d+(?:-P\d+)?$')


def normalize(record: dict) -> dict:
    """Separate dependency types and preserve, but deactivate, old anchor strings."""
    original_refs = record.pop('source_refs', [])
    record['source_refs'] = []
    for ref in original_refs:
        field, value = 'source_refs', ref
        if LEGACY.fullmatch(ref):
            record.setdefault('legacy_source_refs', []).append(ref)
            value = ref.split('#')[0]
        elif not ref.startswith('XP-T-'):
            field = next((field for prefix, field in PREFIXES.items() if ref.startswith(prefix)), 'skill_refs')
        values = record.setdefault(field, [])
        if value not in values:
            values.append(value)
    if 'legacy_source_refs' in record:
        record['legacy_source_refs'] = list(dict.fromkeys(record['legacy_source_refs']))
    return record



class SourceRangeNormalizer:
    """Split ranges only across explicitly verified blank-number slots.

    XP-T-004 numbers its original physical lines, including unnumbered blank
    separators. Never invent an anchor or silently skip a nonblank missing slot.
    """
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.anchors = {int(m[1]): i for i, line in enumerate(self.lines, 1)
                        if (m := re.match(r'^\[XP-T-004#P(\d+)\]', line))}
        self.changes = {}

    def split(self, ref: str) -> list[str]:
        match = re.fullmatch(r'XP-T-004#P(\d+)(?:-P(\d+))?', ref)
        if not match:
            return [ref]
        start, stop = int(match[1]), int(match[2] or match[1])
        if start > stop or start not in self.anchors or stop not in self.anchors:
            raise AssetError(f'{ref}: cannot migrate absent range endpoints')
        missing = set(range(start, stop + 1)) - set(self.anchors)
        if not missing:
            return [ref]
        if any(self.anchors[n] != n for n in self.anchors):
            raise AssetError(f'{ref}: numbering is not verified physical-line numbering')
        for n in missing:
            if n > len(self.lines) or self.lines[n - 1].strip():
                raise AssetError(f'{ref}: absent anchor is not a verified blank separator')
        groups = []
        run = []
        for n in range(start, stop + 1):
            if n in missing:
                if run:
                    groups.append(run); run = []
            else:
                run.append(n)
        if run:
            groups.append(run)
        result = [f'XP-T-004#P{g[0]:03d}' + (f'-P{g[-1]:03d}' if len(g) > 1 else '')
                  for g in groups]
        self.changes[ref] = {'references': result, 'verified_blank_line_slots': sorted(missing)}
        return result

    def record(self, record: dict) -> dict:
        record['source_refs'] = list(dict.fromkeys(
            ref for old in record.get('source_refs', []) for ref in self.split(old)))
        return record


def migrate(root: Path) -> dict:
    root = root.absolute()
    ledger = safe_path(root, '08_ops/migrations/2026-09-05-architecture.json')
    if ledger.exists():
        return {'status': 'already_migrated', 'ledger': ledger.relative_to(root).as_posix()}
    before = {}
    for rel, expected in EXPECTED.items():
        data = safe_path(root, rel).read_bytes()
        if blob_sha(data) != expected:
            raise AssetError(f'Unexpected baseline for {rel}; do not migrate over concurrent edits')
        before[rel] = digest(data)
    compatibility = safe_path(root, '04_skills')
    for path in compatibility.rglob('*'):
        if path.is_file():
            rel = path.relative_to(compatibility).as_posix()
            if path.read_bytes() != safe_path(root, '.agents/skills/' + rel).read_bytes():
                raise AssetError(f'04_skills/{rel} has unique edits; reconcile before migration')
    rows = manifest_rows(root)
    locks = {'schema_version': '1.0', 'sources': {}}
    for row in rows:
        if row['status'] != 'knowledge_extracted':
            continue
        locks['sources'][row['source_id']] = {
            'source_version': row['source_version'], 'raw_path': row['raw_path'],
            'raw_path_sha256': digest(safe_path(root, row['raw_path']).read_bytes()),
            'reviewed_path': row['reviewed_path'],
            'reviewed_path_sha256': digest(safe_path(root, row['reviewed_path']).read_bytes()) if row['reviewed_path'] else '',
            'locator': 'paragraph' if row['source_id'] == 'XP-T-004' else 'file_only',
            'assurance': 'location_checked_not_semantic_verification',
        }
    # Preflight parsing of all files before applying any transformed data.
    transformed = {}
    ranges = SourceRangeNormalizer(read_text(root, '01_source/reviewed/XP-T-004_reviewed.txt'))
    for rel in KINDS.values():
        records = yaml_load(read_text(root, rel))
        transformed[rel] = yaml.safe_dump([ranges.record(normalize(r)) for r in records], allow_unicode=True, sort_keys=False).encode('utf-8')
    cases = jsonl(read_text(root, '06_evals/evals.jsonl'))
    for case in cases:
        ranges.record(normalize(case))
        if case['id'] == 'XP-E-047':
            case['claim_refs'] = []
            case['model_refs'] = ['XP-M-001']
        if case['id'] == 'XP-E-049':
            case['expected_behavior'] = case['expected_behavior'].replace('三段材料', '四个来源')
        if case['id'] == 'XP-E-032':
            case['expected_behavior'] = '可用 XP-T-004 和 career-planning 构建有限职业规划流程；不得复原缺失的十个教练模型，必须区分规划与完整教练技术。'
            case['source_refs'] = ['XP-T-004']
            case['model_refs'] = ['XP-M-001']
            case['skill_refs'] = ['career-planning']
    transformed['06_evals/evals.jsonl'] = b''.join(canonical(c) for c in cases)
    for path in sorted((root / '.agents/skills').glob('*/SKILL.md')):
        if path.parent.name == 'create-readme':
            continue  # third-party development aid is not in runtime packages
        text = path.read_text(encoding='utf-8')
        fm = frontmatter(text); fm['version'] = '0.3.0'
        body = text.split('---', 2)[2].lstrip('\n')
        body = re.sub(r'XP-T-00[123]#P\d+(?:-P\d+)?',
                      lambda m: m[0].split('#')[0] + '（01_source/raw/' + m[0].split('#')[0] + '_raw.txt；仅文件级定位）', body)
        body = re.sub(r'XP-T-004#P\d+(?:-P\d+)?', lambda m: '、'.join(ranges.split(m[0])), body)
        body = body.replace('任何“夏鹏认为”必须带来源锚点。', '任何“夏鹏认为”按公共规则给来源 ID 与真实文件路径；不得补造锚点。')
        if path.parent.name == 'understand-me':
            body = body.replace('`user_profile.md`', '`05_user_private/drafts/user_profile.md`')
            body = body.replace('`profile_facts.jsonl`', '`05_user_private/drafts/profile_facts.jsonl`')
            body = body.replace('`open_questions.md`', '`05_user_private/drafts/open_questions.md`')
            body = body.replace('`weekly_delta.md`', '`05_user_private/drafts/weekly_delta.md`')
        if path.parent.name == 'scene-skill-builder':
            body = '生成文件只能先写入 `08_ops/skill_candidates/<name>/`；经用户审阅、补评测和验证后再进入自动发现目录。\n\n' + body
        if path.parent.name == 'xia-peng-method-router':
            body = ('复合任务只选一个主 Skill，按 `03_agent/skill_registry.json` 补必要辅助能力；复用已授权上下文，禁止无界递归和重复画像收集。\n\n' + body)
        common = ('先读取并遵守 `03_agent/METHOD_POLICY.md`，包括直接显式调用本 Skill 的情况。'
                  '依赖与可选辅助能力见 `03_agent/skill_registry.json`。这是方法流程，不代表已执行任何工具动作。\n\n')
        transformed[path.relative_to(root).as_posix()] = (
            '---\n' + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + '---\n\n' + common + body
        ).encode('utf-8')
    transformed['01_source/source_locks.json'] = canonical(locks)
    for rel, data in transformed.items():
        safe_path(root, rel).write_bytes(data)
    # Eliminate independently editable replicas. The generated equivalents live in dist/.
    shutil.rmtree(compatibility)
    compatibility.mkdir()
    (compatibility / 'README.md').write_text('# 兼容目录已退出编辑流程\n\n唯一 Skill 编辑源为 `.agents/skills/`。运行 `python scripts/assets.py build` 生成 `dist/runtime/`；禁止将本目录反向同步到运行目录。\n', encoding='utf-8')
    for rel in ('02_knowledge/principle_cards.jsonl', 'tests/test_sync_codex_skills.py'):
        path = safe_path(root, rel)
        if path.exists():
            path.unlink()
    ignore = safe_path(root, '.gitignore')
    with ignore.open('a', encoding='utf-8') as handle:
        handle.write('\n# Generated builds and local transactional state\ndist/\n.asset-build-*/\n.dist-backup/\n01_source/.ingestion.lock\n01_source/.intake-*/\n01_source/.manifest-*\n08_ops/skill_candidates/\n')
    log = safe_path(root, 'CHANGELOG.md')
    text = log.read_text(encoding='utf-8')
    insert = ('\n## Unreleased — 架构落地（2026-09-05）\n\n'
              '- .agents/skills 成为唯一编辑源；JSONL、审阅页、黄金题视图和运行包由构建生成。\n'
              '- 引用类型拆分；前三个来源的旧段落编号保留在 legacy_source_refs，不再作为有效引用。\n'
              '- 加入来源哈希锁、JSON Schema、引用/依赖校验、上下文包、行为评测协议和严格发布门禁。\n'
              '- 课程登记增加前置校验、重复 ID/内容检查、写入锁和普通异常回滚。\n'
              '- 公共方法规则独立，支持主流程与辅助 Skill、画像私有路径和候选 Skill 审核。\n'
              '- 新增架构行为题；修正旧题的过期范围与依赖。不宣称模型全量回归已通过。\n')
    log.write_text(text.replace('# Changelog\n', '# Changelog\n' + insert, 1), encoding='utf-8')
    matrix = safe_path(root, '08_ops/MERGE_DECISION_MATRIX.md')
    if matrix.exists():
        matrix.write_text(matrix.read_text(encoding='utf-8').replace('`mentioned`/`partial`', '`external_definition_required` / `partially_observed`'), encoding='utf-8')
    review = safe_path(root, '08_ops/PROJECT_REVIEW.md')
    if review.exists():
        review.write_text('> 本文保留为前次分析记录；当前已实施架构、验收与未决项见 `ARCHITECTURE.md`。\n\n' + review.read_text(encoding='utf-8'), encoding='utf-8')
    unchanged = {}
    for rel in EXPECTED:
        if rel.startswith('01_source/'):
            unchanged[rel] = digest(safe_path(root, rel).read_bytes())
            if unchanged[rel] != before[rel]:
                raise AssetError(f'Source unexpectedly changed: {rel}')
    result = {'schema_version': '1.0', 'baseline_commit': '3a6cbeb2d83f81250e04f0beabd3d20d5f88b6b0',
              'date': '2026-09-05', 'semantic_source_review': 'not_performed',
              'transformation': 'typed dependencies; historical anchors archived; statements not rewritten',
              'verified_range_splits': ranges.changes,
              'before_sha256': before, 'after_sha256': {rel: digest(data) for rel, data in transformed.items()},
              'unchanged_source_sha256': unchanged}
    ledger.parent.mkdir(parents=True, exist_ok=True); ledger.write_bytes(canonical(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--apply', action='store_true', required=True)
    args = parser.parse_args()
    try:
        result = migrate(args.root)
        print('Migration complete; source files preserved. Status:', result.get('status', 'migrated'))
    except (AssetError, OSError, ValueError) as exc:
        raise SystemExit(f'FAIL: {exc}')
