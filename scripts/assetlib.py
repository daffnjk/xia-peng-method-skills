"""Validated, deterministic asset loading. No model calls or network access."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    'principle': '02_knowledge/principle_cards.yaml',
    'case': '02_knowledge/case_cards.yaml',
    'claim': '02_knowledge/claim_audit.yaml',
    'conflict': '02_knowledge/contradictions.yaml',
    'model': '02_knowledge/model_registry.yaml',
}
REF_FIELDS = ('source_refs', 'principle_refs', 'case_refs', 'claim_refs',
              'conflict_refs', 'model_refs', 'skill_refs')
PREFIXES = {'XP-P-': 'principle_refs', 'XP-C-': 'case_refs',
            'XP-CL-': 'claim_refs', 'XP-X-': 'conflict_refs',
            'XP-M-': 'model_refs'}
SOURCE_RE = re.compile(r'^(XP-T-\d{3,})(?:#P(\d{3,})(?:-P(\d{3,}))?)?$')
ANCHOR_RE = re.compile(r'^\[(XP-T-\d{3,})#P(\d{3,})\]', re.M)
DIMENSIONS = ('source_fidelity', 'method_consistency', 'boundary_awareness',
              'actionability', 'uncertainty_handling')


class AssetError(ValueError):
    """Actionable asset validation failure."""


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys rather than silently accepting the last."""


def _mapping(loader: UniqueLoader, node: Any, deep: bool = False) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, (str, int, float, bool, type(None))):
            raise AssetError('YAML mapping keys must be scalar')
        if key in result:
            raise AssetError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def safe_path(root: Path, rel: str) -> Path:
    """Return a repository-relative path, rejecting traversal and all symlinks."""
    if not isinstance(rel, str) or not rel or '\\' in rel:
        raise AssetError(f'Invalid relative path: {rel!r}')
    posix = PurePosixPath(rel)
    if posix.is_absolute() or any(p in ('..', '.', '.git') for p in rel.split('/')):
        raise AssetError(f'Unsafe relative path: {rel}')
    root = root.absolute()
    current = root
    if current.is_symlink():
        raise AssetError(f'Symlink root: {root}')
    for part in posix.parts:
        current = current / part
        if current.is_symlink():
            raise AssetError(f'Symlink not allowed: {rel}')
    if not current.resolve().is_relative_to(root.resolve()):
        raise AssetError(f'Path escaped root: {rel}')
    return current


def read_text(root: Path, rel: str) -> str:
    try:
        return safe_path(root, rel).read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as exc:
        raise AssetError(f'{rel}: {exc}') from exc


def yaml_load(text: str) -> Any:
    try:
        return yaml.load(text, Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise AssetError(f'Invalid YAML: {exc}') from exc


def _pairs(pairs: list) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise AssetError(f'Duplicate JSON key: {key}')
        obj[key] = value
    return obj


def json_load(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(AssetError(f'Invalid number: {x}')))
    except json.JSONDecodeError as exc:
        raise AssetError(f'Invalid JSON: {exc}') from exc


def jsonl(text: str) -> list[dict]:
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip():
            item = json_load(line)
            if not isinstance(item, dict):
                raise AssetError(f'JSONL line {number} must be an object')
            result.append(item)
    return result


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def record_id(record: dict) -> str:
    return record.get('id', record.get('model_id', ''))


def frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise AssetError('Skill must start with YAML frontmatter delimiter')
    try:
        end = lines.index('---', 1)
    except ValueError as exc:
        raise AssetError('Skill frontmatter is not closed') from exc
    data = yaml_load('\n'.join(lines[1:end]))
    if not isinstance(data, dict):
        raise AssetError('Skill frontmatter must be a mapping')
    return data


def manifest_rows(root: Path) -> list[dict]:
    reader = csv.DictReader(io.StringIO(read_text(root, '01_source/manifest.csv')))
    fields = reader.fieldnames or []
    required = {'source_id', 'raw_path', 'reviewed_path', 'rights_status', 'status', 'source_version'}
    if len(set(fields)) != len(fields) or not required.issubset(fields):
        raise AssetError('Manifest has duplicate or missing required columns')
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise AssetError('Manifest row width does not match header')
    return rows


class Catalog:
    """One catalog used by validation, retrieval, builds and evaluation tooling."""

    def __init__(self, root: Path = ROOT):
        self.root = root.absolute()
        self.schema = json_load(read_text(root, 'schemas/assets.schema.json'))
        Draft202012Validator.check_schema(self.schema)
        self.records: dict[str, dict] = {}
        self.by_kind: dict[str, list[dict]] = {}
        self.sources: dict[str, dict] = {}
        self.skills: dict[str, dict] = {}
        self.evals: list[dict] = []
        self.warnings: list[str] = []
        self.inputs: set[str] = {'schemas/assets.schema.json', '01_source/manifest.csv',
                                '01_source/source_locks.json', '03_agent/skill_registry.json',
                                '03_agent/METHOD_POLICY.md', 'requirements-dev.txt',
                                'scripts/assetlib.py', 'scripts/assets.py'}
        self._load()
        self._snapshot = self._current_fingerprints()

    def check(self, obj: Any, kind: str, label: str) -> None:
        schema = {'$ref': f'#/$defs/{kind}', '$defs': self.schema['$defs']}
        errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: str(e.path))
        if errors:
            raise AssetError(f'{label}: {errors[0].message}')

    def _load(self) -> None:
        locks = json_load(read_text(self.root, '01_source/source_locks.json'))
        self.check(locks, 'locks', 'source_locks')
        for row in manifest_rows(self.root):
            sid = row['source_id']
            self.check(row, 'source', sid)
            if sid in self.sources:
                raise AssetError(f'Duplicate source ID: {sid}')
            self.sources[sid] = row
            if row['status'] != 'knowledge_extracted':
                continue  # inbox is registered, but not a production evidence source
            if not row['raw_path'].startswith('01_source/raw/'):
                raise AssetError(f'{sid}: published source must be in 01_source/raw/')
            if sid not in locks['sources']:
                raise AssetError(f'{sid}: missing source lock; review and lock before use')
            lock = locks['sources'][sid]
            if lock['source_version'] != row['source_version']:
                raise AssetError(f'{sid}: source version differs from lock')
            for field in ('raw_path', 'reviewed_path'):
                rel = row[field]
                if rel:
                    if field == 'reviewed_path' and not rel.startswith('01_source/reviewed/'):
                        raise AssetError(f'{sid}: invalid reviewed path')
                    self.inputs.add(rel)
                    data = safe_path(self.root, rel).read_bytes()
                    if lock.get(field) != rel or digest(data) != lock.get(field + '_sha256'):
                        raise AssetError(f'{sid}: source lock mismatch for {field}')
            row['_locator'] = lock['locator']
            if row['_locator'] == 'paragraph':
                if not row['reviewed_path']:
                    raise AssetError(f'{sid}: paragraph source needs a reviewed file')
                text = read_text(self.root, row['reviewed_path'])
                anchors = ANCHOR_RE.findall(text)
                numbers = [int(n) for s, n in anchors if s == sid]
                if len(numbers) != len(set(numbers)) or not numbers or min(numbers) < 1:
                    raise AssetError(f'{sid}: duplicate or missing anchors')
                if any(s != sid for s, _ in anchors):
                    raise AssetError(f'{sid}: foreign source anchor')
                row['_anchors'] = set(numbers)
        if set(locks['sources']) - set(self.sources):
            raise AssetError('Source locks contain an unknown source')
        for kind, rel in KINDS.items():
            self.inputs.add(rel)
            records = yaml_load(read_text(self.root, rel))
            if not isinstance(records, list) or not records:
                raise AssetError(f'{rel}: expected a non-empty record list')
            self.by_kind[kind] = records
            for record in records:
                self.check(record, kind, rel)
                rid = record_id(record)
                if rid in self.records:
                    raise AssetError(f'Duplicate knowledge ID: {rid}')
                self.records[rid] = record
        registry = json_load(read_text(self.root, '03_agent/skill_registry.json'))
        self.check(registry, 'registry', 'skill_registry')
        for skill in registry['skills']:
            name = skill['name']
            if name in self.skills:
                raise AssetError(f'Duplicate Skill: {name}')
            rel = f'.agents/skills/{name}/SKILL.md'
            self.inputs.add(rel)
            text = read_text(self.root, rel)
            fm = frontmatter(text)
            self.check(fm, 'frontmatter', name)
            if fm['name'] != name or fm.get('version') != skill['version']:
                raise AssetError(f'{name}: frontmatter/registry mismatch')
            if '03_agent/METHOD_POLICY.md' not in text:
                raise AssetError(f'{name}: missing shared policy dependency')
            refs = re.findall(r'XP-T-\d{3,}(?:#P\d{3,}(?:-P\d{3,})?)?', text)
            for ref in refs:
                self.resolve(ref)
            cited = {r.split('#')[0] for r in refs}
            if cited != set(skill.get('source_refs', [])):
                raise AssetError(f'{name}: body citations {sorted(cited)} != registry source_refs '
                                 f'{sorted(skill.get("source_refs", []))}')
            for resource in skill.get('resources', []):
                if PurePosixPath(resource).parts[0] not in ('references', 'scripts', 'assets'):
                    raise AssetError(f'{name}: resource must be under references/scripts/assets')
                if PurePosixPath(resource).suffix.lower() not in ('.md', '.txt', '.py', '.json', '.yaml'):
                    raise AssetError(f'{name}: unsupported resource type')
                resource_rel = f'.agents/skills/{name}/{resource}'
                safe_path(self.root, resource_rel)
                self.inputs.add(resource_rel)
            self.skills[name] = skill
        skills_dir = safe_path(self.root, '.agents/skills')
        discovered = {p.parent.name for p in skills_dir.glob('*/SKILL.md')}
        extra = discovered - set(self.skills) - set(registry.get('development_skills', []))
        if extra:
            raise AssetError('Unregistered discoverable Skills: ' + ', '.join(sorted(extra)))
        for path in sorted(safe_path(self.root, '06_evals').glob('*.jsonl')):
            self.inputs.add(path.relative_to(self.root).as_posix())
            self.evals.extend(jsonl(path.read_text(encoding='utf-8-sig')))
        if not self.evals:
            raise AssetError('No evaluation cases found')
        ids = set()
        for record in self.evals:
            self.check(record, 'eval', 'evaluation')
            if record['id'] in ids:
                raise AssetError(f'Duplicate evaluation ID: {record["id"]}')
            ids.add(record['id'])
        for item in list(self.records.values()) + self.evals + list(self.skills.values()):
            self.check_refs(item)
        self._check_graph()
        file_only = sorted(s for s, row in self.sources.items() if row.get('_locator') == 'file_only')
        if file_only:
            self.warnings.append('File-level evidence only (not precise paragraph support): ' + ', '.join(file_only))

    def resolve(self, ref: str) -> dict:
        match = SOURCE_RE.fullmatch(ref)
        if not match or match[1] not in self.sources:
            raise AssetError(f'Unknown/malformed source reference: {ref}')
        sid, first, last = match.groups()
        source = self.sources[sid]
        if source['status'] != 'knowledge_extracted':
            raise AssetError(f'{ref}: source is staged, not integrated')
        locator = source.get('_locator')
        result = {'source_id': sid, 'source_version': source['source_version'],
                  'path': source['reviewed_path'] if first else source['raw_path'],
                  'locator': 'paragraph' if first else 'file_only'}
        if first:
            if locator != 'paragraph':
                raise AssetError(f'{ref}: historical/unverified anchor; cite source ID + raw path instead')
            start, stop = int(first), int(last or first)
            if start < 1 or start > stop or stop - start > 10000:
                raise AssetError(f'{ref}: invalid paragraph range')
            if not set(range(start, stop + 1)).issubset(source['_anchors']):
                raise AssetError(f'{ref}: missing paragraph anchor')
            result.update(start=start, end=stop)
        return result

    def check_refs(self, item: dict) -> None:
        expected = {'principle_refs': 'XP-P-', 'case_refs': 'XP-C-', 'claim_refs': 'XP-CL-',
                    'conflict_refs': 'XP-X-', 'model_refs': 'XP-M-'}
        for field in REF_FIELDS:
            refs = item.get(field, [])
            if not isinstance(refs, list) or any(not isinstance(r, str) for r in refs):
                raise AssetError(f'{record_id(item)}: invalid {field}')
            if len(set(refs)) != len(refs):
                raise AssetError(f'{record_id(item)}: duplicate {field}')
            for ref in refs:
                if field == 'source_refs':
                    self.resolve(ref)
                elif field == 'skill_refs':
                    if ref not in self.skills:
                        raise AssetError(f'Unknown Skill dependency: {ref}')
                elif ref not in self.records or not ref.startswith(expected[field]):
                    raise AssetError(f'Unknown or mistyped {field}: {ref}')

    def _check_graph(self) -> None:
        def visit(name: str, ancestors: set[str]) -> None:
            if name in ancestors:
                raise AssetError(f'Cyclic Skill dependency: {name}')
            for child in self.skills[name].get('skill_refs', []):
                visit(child, ancestors | {name})
        for name in self.skills:
            visit(name, set())

    def _current_fingerprints(self) -> dict[str, str]:
        return {rel: digest(safe_path(self.root, rel).read_bytes()) for rel in sorted(self.inputs)}

    def fingerprints(self) -> dict[str, str]:
        current = self._current_fingerprints()
        if current != self._snapshot:
            raise AssetError('Assets changed after validation; reload before building or evaluating')
        return current

    def identity(self) -> str:
        return digest(canonical(self.fingerprints()))

    def strict_evidence(self) -> None:
        for record in list(self.records.values()) + self.evals:
            for ref in record.get('source_refs', []):
                if self.resolve(ref)['locator'] != 'paragraph':
                    raise AssetError('Strict evidence gate: file-level citations still need human-verified locators')

    def context(self, skill: str, query: str = '', limit: int = 8) -> dict:
        if skill not in self.skills:
            raise AssetError(f'Unknown Skill: {skill}')
        if not 1 <= limit <= 50:
            raise AssetError('limit must be between 1 and 50')
        source_ids = {r.split('#')[0] for r in self.skills[skill]['source_refs']}
        def related(item: dict) -> bool:
            return bool(source_ids & {r.split('#')[0] for r in item.get('source_refs', [])})
        tokens = set(re.findall(r'[\w-]+', query.lower()))
        candidates = [r for kind in ('principle', 'case') for r in self.by_kind[kind] if related(r)]
        candidates.sort(key=lambda r: (-sum(t in json.dumps(r, ensure_ascii=False).lower() for t in tokens), record_id(r)))
        selected = candidates[:limit]
        governance = [r for kind in ('claim', 'conflict', 'model') for r in self.by_kind[kind] if related(r)]
        refs = sorted({ref for r in selected + governance for ref in r.get('source_refs', [])})
        return {'asset_digest': self.identity(), 'primary_skill': skill,
                'support_skills': self.skills[skill].get('skill_refs', []),
                'policy_path': '03_agent/METHOD_POLICY.md', 'knowledge': selected,
                'governance': governance, 'source_locations': [self.resolve(r) for r in refs],
                'link_basis': 'conservative shared-source association; not a semantic entailment judgment',
                'execution': 'context preparation only; no tool actions or profile reads'}
