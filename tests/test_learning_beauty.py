"""Book asset contracts, not model-behavior or independent semantic tests."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from assetlib import Catalog, digest, frontmatter
from assets import runtime_files


class LearningBeautyAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog(ROOT)
        cls.provenance = json.loads((ROOT / '01_source/XP-T-005_provenance.json').read_text(encoding='utf-8'))
        cls.cards = {r['id']: r for r in cls.catalog.by_kind['principle']
                     if any(s.startswith('XP-T-005#') for s in r['source_refs'])}

    def test_source_identity_and_preserved_bytes(self):
        p = self.provenance
        self.assertEqual(p['author'], '刘澜')
        self.assertEqual(p['original_pdf']['pdf_spreads'], 202)
        self.assertEqual(p['original_pdf']['sha256'],
                         '0bbd0f3da5f19ab3807c4e0c7eccead977fddc341d9bf1df6834705091f24a53')
        self.assertFalse(p['original_pdf']['uploaded_to_repository'])
        self.assertIsNone(p['human_semantic_reviewer'])
        self.assertEqual(p['rights_status'], 'internal_only_pending_confirmation')
        self.assertEqual(self.catalog.sources['XP-T-005']['rights_status'], p['rights_status'])
        for role in ('raw', 'reviewed'):
            data = (ROOT / p['records'][role + '_path']).read_bytes()
            self.assertEqual(digest(data), p['records'][role + '_sha256'])
            self.assertIn(p['original_pdf']['sha256'].encode(), data)
        self.assertEqual(p['records']['raw_sha256'], p['records']['reviewed_sha256'])

    def test_all_24_mappings_resolve_to_attributed_cards(self):
        self.assertEqual(set(self.cards), {f'XP-P-{n:03}' for n in range(49, 73)})
        maps = self.provenance['mappings']
        self.assertEqual(len(maps), 24)
        self.assertEqual({m['source_ref'] for m in maps}, {f'XP-T-005#P{n:03}' for n in range(1, 25)})
        for m in maps:
            with self.subTest(ref=m['source_ref']):
                card = self.cards[m['principle_id']]
                self.assertEqual(card['author'], '刘澜')
                self.assertEqual(card['source_kind'], 'external_book')
                self.assertIn(m['source_ref'], card['source_refs'])
                self.assertEqual(card['source_pages']['printed'], m['printed'])
                self.assertEqual(card['source_pages']['pdf_spreads'], m['pdf_spreads'])
                self.assertEqual(self.catalog.resolve(m['source_ref'])['path'],
                                 self.provenance['records']['reviewed_path'])
                self.assertTrue(all(1 <= page <= 202 for page in m['pdf_spreads']))

    def test_source_terminology_and_operator_contract(self):
        model = lambda n: self.cards[f'XP-P-{n:03}']['model_definition']
        self.assertEqual(model(49)['五项修炼'], ['反学习', '参考答案思维方式', '聚焦', '模式化学习', '学习迁移'])
        self.assertEqual(model(64)['四问'], ['我听到什么？', '我想到什么？', '我变成什么？', '我用到哪里？'])
        self.assertEqual(model(63), {'应用性迁移': 'X→A', '近迁移': 'A(→X)→B',
                                     '远迁移': 'A→X→B', '创造性迁移': '(A→)X→Y→B'})
        self.assertEqual(model(57)['目标聚焦_对象发散'], '小偷式')
        self.assertEqual(model(57)['目标发散_对象聚焦'], '苏东坡式')
        self.assertEqual([len(model(n)[key]) for n, key in
                          ((66, '八个技巧'), (67, '三个技巧'), (68, '八个技巧'), (69, '三个技巧'))], [8, 3, 8, 3])
        self.assertEqual(len(model(71)['公式']), 18)
        self.assertEqual(model(71)['公式'][12], '学习=我知道∩我不知道')

    def test_new_eval_definitions_cover_cards_without_duplicate_ids(self):
        cases = [r for r in self.catalog.evals if 75 <= int(r['id'].split('-')[-1]) <= 98]
        self.assertEqual({r['id'] for r in cases}, {f'XP-E-{n:03}' for n in range(75, 99)})
        self.assertEqual(len(cases), 24)
        self.assertEqual({p for r in cases for p in r.get('principle_refs', [])}, set(self.cards))
        self.assertTrue(all(r['skill_refs'] == ['xia-peng-method-router'] for r in cases))
        for r in cases:
            self.assertTrue(r['expected_behavior'])
            self.assertTrue(r['forbidden_behavior'])
            self.assertEqual(len(r['score_dimensions']), 5)
            self.assertTrue(all(s.startswith('XP-T-005#') for s in r['source_refs']))

    def test_candidate_is_not_enabled_and_uses_canonical_evals(self):
        name = 'book-learning-transfer'
        text = (ROOT / f'08_ops/skill_candidates/{name}/SKILL.md').read_text(encoding='utf-8')
        self.assertEqual(frontmatter(text)['status'], 'candidate')
        self.assertNotIn(name, self.catalog.skills)
        self.assertFalse((ROOT / f'.agents/skills/{name}/SKILL.md').exists())
        self.assertIn('06_evals/learning_beauty_evals.jsonl', text)
        self.assertNotIn('本目录 `evals.jsonl`', text)
        self.assertIn('不是描述自己成为哪类人', text)

    def test_runtime_includes_evidence_but_excludes_review_assets(self):
        files = runtime_files(self.catalog)
        for role in ('raw', 'reviewed'):
            self.assertIn(self.provenance['records'][role + '_path'], files)
        self.assertNotIn('01_source/XP-T-005_provenance.json', files)
        self.assertIn('仓库维护索引', self.provenance['runtime_scope'])
        self.assertFalse(any(path.startswith(('06_evals/', '08_ops/', '05_user_private/', '01_source/inbox/', 'tests/')) for path in files))
        self.assertFalse(any(path.lower().endswith('.pdf') for path in files))
        for r in self.catalog.evals:
            if 75 <= int(r['id'].split('-')[-1]) <= 98:
                self.assertFalse(any(r['expected_behavior'].encode('utf-8') in value for value in files.values()))

    def test_router_context_retrieves_external_book_without_eval_answers(self):
        result = self.catalog.context('xia-peng-method-router', query='四问', limit=50)
        selected = {r['id']: r for r in result['knowledge']}
        self.assertIn('XP-P-064', selected)
        self.assertEqual(selected['XP-P-064']['author'], '刘澜')
        self.assertNotIn('expected_behavior', json.dumps(result, ensure_ascii=False))

    def test_synthetic_fixture_ignores_production_registry_changes(self):
        import test_assets
        with tempfile.TemporaryDirectory() as tmp:
            template = Path(tmp) / 'template'
            target = Path(tmp) / 'fixture'
            for rel in ('schemas/assets.schema.json', 'requirements-dev.txt', 'scripts/assetlib.py',
                        'scripts/assets.py', 'tests/fixtures/skill_registry.json'):
                dest = template / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, dest)
            (template / '03_agent').mkdir()
            (template / '03_agent/skill_registry.json').write_text('not a valid production registry', encoding='utf-8')
            (template / '03_agent/METHOD_POLICY.md').write_text('PRODUCTION_SENTINEL', encoding='utf-8')
            with patch.object(test_assets, 'ROOT', template):
                test_assets.fixture(target)
            catalog = Catalog(target)
            self.assertEqual(len(catalog.sources), 4)
            self.assertEqual(len(catalog.skills), 7)
            self.assertNotIn('PRODUCTION_SENTINEL', (target / '03_agent/METHOD_POLICY.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
