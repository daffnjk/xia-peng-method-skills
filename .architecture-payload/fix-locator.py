from pathlib import Path
root = Path.cwd()
p = root / 'scripts/migrate_architecture.py'
s = p.read_text(encoding='utf-8')
anchor = '\ndef migrate(root: Path) -> dict:\n'
assert s.count(anchor) == 1
helper = '''
class SourceRangeNormalizer:
    """Split ranges only across explicitly verified blank-number slots.

    XP-T-004 numbers its original physical lines, including unnumbered blank
    separators. Never invent an anchor or silently skip a nonblank missing slot.
    """
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.anchors = {int(m[1]): i for i, line in enumerate(self.lines, 1)
                        if (m := re.match(r'^\\[XP-T-004#P(\\d+)\\]', line))}
        self.changes = {}

    def split(self, ref: str) -> list[str]:
        match = re.fullmatch(r'XP-T-004#P(\\d+)(?:-P(\\d+))?', ref)
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

'''
s = s.replace(anchor, '\n' + helper + anchor)
s = s.replace('    transformed = {}\n', "    transformed = {}\n    ranges = SourceRangeNormalizer(read_text(root, '01_source/reviewed/XP-T-004_reviewed.txt'))\n", 1)
s = s.replace('[normalize(r) for r in records]', '[ranges.record(normalize(r)) for r in records]')
s = s.replace('        normalize(case)\n', '        ranges.record(normalize(case))\n')
s = s.replace("        body = body.replace('任何", "        body = re.sub(r'XP-T-004#P\\d+(?:-P\\d+)?', lambda m: '、'.join(ranges.split(m[0])), body)\n        body = body.replace('任何", 1)
s = s.replace("'before_sha256': before,", "'verified_range_splits': ranges.changes,\n              'before_sha256': before,")
p.write_text(s, encoding='utf-8')
(root / 'tests/test_locator_migration.py').write_text('''"""Regression coverage for verified blank separators in the real source format."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from assetlib import AssetError
from migrate_architecture import SourceRangeNormalizer


class LocatorMigrationTests(unittest.TestCase):
    def test_split_verified_blank_without_inventing_anchor(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\\n\\n[XP-T-004#P003] C\\n')
        self.assertEqual(ranges.split('XP-T-004#P001-P003'), ['XP-T-004#P001', 'XP-T-004#P003'])
        self.assertEqual(ranges.changes['XP-T-004#P001-P003']['verified_blank_line_slots'], [2])

    def test_nonblank_gap_rejected(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\\nUnanchored text\\n[XP-T-004#P003] C\\n')
        with self.assertRaises(AssetError):
            ranges.split('XP-T-004#P001-P003')

    def test_missing_endpoint_rejected(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\\n\\n[XP-T-004#P003] C\\n')
        with self.assertRaises(AssetError):
            ranges.split('XP-T-004#P001-P002')

    def test_unknown_numbering_rejected(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\\n\\n[XP-T-004#P004] D\\n')
        with self.assertRaises(AssetError):
            ranges.split('XP-T-004#P001-P004')

    def test_contiguous_unchanged(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\\n[XP-T-004#P002] B\\n')
        self.assertEqual(ranges.split('XP-T-004#P001-P002'), ['XP-T-004#P001-P002'])
        self.assertEqual(ranges.changes, {})
''', encoding='utf-8')
print('Applied source-range migration and regression coverage; validator remains strict.')
