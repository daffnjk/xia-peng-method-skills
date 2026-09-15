"""Regression coverage for verified blank separators in the real source format."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from assetlib import AssetError
from migrate_architecture import SourceRangeNormalizer


class LocatorMigrationTests(unittest.TestCase):
    def test_split_verified_blank_without_inventing_anchor(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\n\n[XP-T-004#P003] C\n')
        self.assertEqual(ranges.split('XP-T-004#P001-P003'), ['XP-T-004#P001', 'XP-T-004#P003'])
        self.assertEqual(ranges.changes['XP-T-004#P001-P003']['verified_blank_line_slots'], [2])

    def test_nonblank_gap_rejected(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\nUnanchored text\n[XP-T-004#P003] C\n')
        with self.assertRaises(AssetError):
            ranges.split('XP-T-004#P001-P003')

    def test_missing_endpoint_rejected(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\n\n[XP-T-004#P003] C\n')
        with self.assertRaises(AssetError):
            ranges.split('XP-T-004#P001-P002')

    def test_unknown_numbering_rejected(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\n\n[XP-T-004#P004] D\n')
        with self.assertRaises(AssetError):
            ranges.split('XP-T-004#P001-P004')

    def test_contiguous_unchanged(self):
        ranges = SourceRangeNormalizer('[XP-T-004#P001] A\n[XP-T-004#P002] B\n')
        self.assertEqual(ranges.split('XP-T-004#P001-P002'), ['XP-T-004#P001-P002'])
        self.assertEqual(ranges.changes, {})
