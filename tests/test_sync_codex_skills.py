"""Standard-library regression tests; no model calls or course data required."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.sync_codex_skills import copy_atomic, main


class SyncSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "04_skills" / "example" / "SKILL.md"
        self.target = self.root / ".agents" / "skills" / "example" / "SKILL.md"
        self.write(self.source, "source\n")

    @staticmethod
    def write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_sync(self, *args):
        with redirect_stdout(StringIO()):
            return main(["--root", str(self.root), *args])

    def symlink(self, link, target, directory=False):
        link.parent.mkdir(parents=True, exist_ok=True)
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this platform")

    def test_create_missing_target(self):
        self.assertEqual(self.run_sync(), 0)
        self.assertEqual(self.target.read_bytes(), self.source.read_bytes())

    def test_check_missing_target_is_read_only(self):
        self.assertEqual(self.run_sync("--check"), 1)
        self.assertFalse((self.root / ".agents").exists())

    def test_dry_run_is_read_only(self):
        self.assertEqual(self.run_sync("--dry-run"), 0)
        self.assertFalse((self.root / ".agents").exists())

    def test_check_equal_files_passes(self):
        self.write(self.target, "source\n")
        self.assertEqual(self.run_sync("--check"), 0)

    def test_unchanged_file_is_not_rewritten(self):
        self.write(self.target, "source\n")
        with patch("scripts.sync_codex_skills.copy_atomic") as copy:
            self.assertEqual(self.run_sync(), 0)
            copy.assert_not_called()

    def test_default_refuses_changed_file(self):
        self.write(self.target, "runtime edit\n")
        self.assertEqual(self.run_sync(), 1)
        self.assertEqual(self.target.read_text(), "runtime edit\n")

    def test_preflight_prevents_partial_sync_on_conflict(self):
        self.write(self.root / "04_skills" / "aaa" / "SKILL.md", "new skill")
        self.write(self.target, "runtime edit\n")
        self.assertEqual(self.run_sync(), 1)
        self.assertFalse((self.root / ".agents" / "skills" / "aaa").exists())

    def test_force_replaces_changed_file(self):
        self.write(self.target, "runtime edit\n")
        self.assertEqual(self.run_sync("--force"), 0)
        self.assertEqual(self.target.read_bytes(), self.source.read_bytes())

    def test_check_changed_file_is_read_only(self):
        self.write(self.target, "runtime edit\n")
        self.assertEqual(self.run_sync("--check"), 1)
        self.assertEqual(self.target.read_text(), "runtime edit\n")

    def test_force_preserves_runtime_only_files_and_skills(self):
        extra = self.target.parent / "local-notes.md"
        standalone = self.target.parents[1] / "create-readme" / "SKILL.md"
        self.write(extra, "keep resource")
        self.write(standalone, "keep skill")
        self.write(self.target, "old")
        self.assertEqual(self.run_sync("--force"), 0)
        self.assertEqual(extra.read_text(), "keep resource")
        self.assertEqual(standalone.read_text(), "keep skill")
        self.assertEqual(self.run_sync("--check"), 0)

    def test_nested_resources_are_copied(self):
        resource = self.source.parent / "references" / "example.txt"
        self.write(resource, "resource")
        self.assertEqual(self.run_sync(), 0)
        self.assertEqual((self.target.parent / "references" / "example.txt").read_text(), "resource")

    def test_missing_source_directory_fails(self):
        self.source.unlink()
        self.source.parent.rmdir()
        self.source.parents[1].rmdir()
        self.assertEqual(self.run_sync(), 1)
        self.assertFalse((self.root / ".agents").exists())

    def test_empty_source_directory_fails(self):
        self.source.unlink()
        self.assertEqual(self.run_sync(), 1)
        self.assertFalse((self.root / ".agents").exists())

    def test_destination_directory_collision_fails(self):
        self.target.mkdir(parents=True)
        self.assertEqual(self.run_sync("--force"), 1)
        self.assertTrue(self.target.is_dir())

    def test_destination_parent_file_collision_fails(self):
        self.write(self.root / ".agents", "not a directory")
        self.assertEqual(self.run_sync("--force"), 1)
        self.assertEqual((self.root / ".agents").read_text(), "not a directory")

    def test_source_symlink_fails(self):
        self.symlink(self.source.parent / "linked.txt", self.source)
        self.assertEqual(self.run_sync("--force"), 1)
        self.assertFalse((self.root / ".agents").exists())

    def test_target_file_symlink_fails(self):
        outside = self.root / "outside.txt"
        self.write(outside, "keep")
        self.symlink(self.target, outside)
        self.assertEqual(self.run_sync("--force"), 1)
        self.assertEqual(outside.read_text(), "keep")

    def test_target_parent_symlink_fails(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.symlink(self.root / ".agents", outside, directory=True)
        self.assertEqual(self.run_sync("--force"), 1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_source_directory_symlink_fails(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.symlink(self.source.parent / "references", outside, directory=True)
        self.assertEqual(self.run_sync("--force"), 1)
        self.assertFalse((self.root / ".agents").exists())

    def test_atomic_copy_failure_preserves_old_file(self):
        self.write(self.target, "keep")
        with patch("scripts.sync_codex_skills.shutil.copy2", side_effect=OSError("copy failed")):
            with self.assertRaises(OSError):
                copy_atomic(self.source, self.target)
        self.assertEqual(self.target.read_text(), "keep")
        self.assertEqual(list(self.target.parent.glob(".skill-sync-*")), [])


if __name__ == "__main__":
    unittest.main()
