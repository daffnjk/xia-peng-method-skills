"""Offline checks for the eval adapter's context pack (no network, synthetic cards)."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'scripts' / 'eval_adapter.py'

spec = importlib.util.spec_from_file_location('eval_adapter', ADAPTER)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def runtime_fixture(root: Path) -> None:
    (root / '03_agent').mkdir(parents=True)
    (root / '03_agent/METHOD_POLICY.md').write_text('# policy\n', encoding='utf-8')
    (root / '02_knowledge').mkdir(parents=True)
    (root / '02_knowledge/principle_cards.yaml').write_text(
        '- id: XP-P-001\n  title: 场景四要素\n  statement: 场景痛点结果模型\n  source_refs: [XP-T-002]\n'
        '- id: XP-P-002\n  title: 无关卡片\n  statement: 完全不相关的厨艺内容\n  source_refs: [XP-T-002]\n',
        encoding='utf-8')


class ContextPackTests(unittest.TestCase):
    def test_selects_matching_card_and_reports_refs(self):
        with tempfile.TemporaryDirectory() as td:
            old = os.getcwd()
            os.chdir(td)
            try:
                runtime_fixture(Path(td))
                system, refs = adapter.context_pack('什么是场景四要素模型')
                self.assertIn('XP-P-001', system)
                self.assertNotIn('XP-P-002', refs)
                self.assertIn('XP-P-001', refs)
                self.assertIn('XP-T-002', refs)
            finally:
                os.chdir(old)

    def test_self_test_protocol_shape(self):
        with tempfile.TemporaryDirectory() as td:
            old = os.getcwd()
            os.chdir(td)
            try:
                runtime_fixture(Path(td))
                proc = subprocess.run([sys.executable, str(ADAPTER), '--self-test'],
                                      capture_output=True, check=True)
                answer = json.loads(proc.stdout.decode('utf-8'))
                self.assertTrue(answer['answer'])
                self.assertIn('XP-T-002', answer['retrieved_refs'])
            finally:
                os.chdir(old)


if __name__ == '__main__':
    unittest.main()
