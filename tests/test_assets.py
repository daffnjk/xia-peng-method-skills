"""Deterministic regression tests using synthetic, non-personal fixtures only."""
from __future__ import annotations

import copy
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import assetlib
import assets
import scaffold_new_course as intake
from assetlib import AssetError, Catalog, canonical, digest, yaml_load
import yaml


def put(root: Path, rel: str, value: str | bytes) -> Path:
    p = root / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(value.encode('utf-8') if isinstance(value, str) else value)
    return p


def dump(root: Path, rel: str, value) -> Path:
    return put(root, rel, canonical(value))


def _can_symlink() -> bool:
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / 't'; target.touch()
        try: (Path(td) / 'l').symlink_to(target)
        except (OSError, NotImplementedError): return False
        return True


SYMLINKS_AVAILABLE = _can_symlink()


def fixture(root: Path) -> None:
    for rel in ('schemas/assets.schema.json',
                'requirements-dev.txt', 'scripts/assetlib.py', 'scripts/assets.py'):
        put(root, rel, (ROOT / rel).read_bytes())
    # Synthetic source IDs and Skill versions must not follow production assets.
    put(root, '03_agent/skill_registry.json', (ROOT / 'tests/fixtures/skill_registry.json').read_bytes())
    put(root, '03_agent/METHOD_POLICY.md', '# Synthetic policy\n\nDo not claim behavior evaluation.\n')
    records = {
        'principle': [{'id':'XP-P-001','title':'原则','statement':'来源观点，不承诺结果',
                       'evidence_type':'explicit','confidence':'high','when_to_use':['规划'],
                       'procedure':['验证'],'guardrails':['不保证'],'source_refs':['XP-T-001']}],
        'case': [{'id':'XP-C-001','title':'案例','summary':'未知结果','source_refs':['XP-T-001']}],
        'claim': [{'id':'XP-CL-001','claim':'一定成功','classification':'guarantee',
                   'use_policy':'不得承诺','source_refs':['XP-T-001','XP-T-004#P001']}],
        'conflict': [{'id':'XP-X-001','topic':'冲突','observations':['快','慢'],
                      'resolution':'区分场景','source_refs':['XP-T-004#P001-P003']}],
        'model': [{'model_id':'XP-M-001','name':'十模型','source_definition':'未提供',
                   'status':'missing_source','source_refs':['XP-T-002']}],
    }
    for kind, rel in assetlib.KINDS.items():
        put(root, rel, yaml.safe_dump(records[kind], allow_unicode=True, sort_keys=False))
    rows, locks = [], {'schema_version':'1.0','sources':{}}
    for n in range(1,5):
        sid = f'XP-T-{n:03}'
        row = dict.fromkeys(intake.FIELDS, '')
        row.update(source_id=sid,title=f'课程{n}',source_type='transcript',raw_path=f'01_source/raw/{sid}_raw.txt',
                   rights_status='not_recorded',status='knowledge_extracted',source_version='1.0')
        raw = put(root, row['raw_path'], f'原稿 {sid}\n')
        reviewed_hash = ''
        if n == 4:
            row['reviewed_path'] = f'01_source/reviewed/{sid}_reviewed.txt'
            reviewed = put(root, row['reviewed_path'], ''.join(f'[{sid}#P{i:03}] 片段{i}\n' for i in range(1,4)))
            reviewed_hash = digest(reviewed.read_bytes())
        rows.append(row)
        locks['sources'][sid] = dict(source_version='1.0',raw_path=row['raw_path'],raw_path_sha256=digest(raw.read_bytes()),
            reviewed_path=row['reviewed_path'],reviewed_path_sha256=reviewed_hash,
            locator='paragraph' if n==4 else 'file_only',assurance='location_checked_not_semantic_verification')
    stream = io.StringIO(); writer=csv.DictWriter(stream,fieldnames=intake.FIELDS,lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    put(root, '01_source/manifest.csv', stream.getvalue()); dump(root,'01_source/source_locks.json',locks)
    registry=json.loads((root/'03_agent/skill_registry.json').read_text())
    for skill in registry['skills']:
        put(root,f'.agents/skills/{skill["name"]}/SKILL.md',
            f'---\nname: {skill["name"]}\ndescription: 测试任务\nversion: {skill["version"]}\n---\n\n遵守 03_agent/METHOD_POLICY.md\n\n来源：{" ".join(skill.get("source_refs", []))}\n')
    evals=[dict(id=f'XP-E-{n:03}',category='source_recall',prompt=f'问题{n}',
                expected_behavior='PRIVATE_EXPECTED_SENTINEL',forbidden_behavior='禁止编造',
                score_dimensions=list(assetlib.DIMENSIONS),source_refs=['XP-T-001']) for n in (1,2)]
    put(root,'06_evals/evals.jsonl',b''.join(canonical(e) for e in evals))
    put(root,'.gitignore','05_user_private/*\n'); put(root,'CHANGELOG.md','# Changelog\n')


class Base(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); fixture(self.root)
    def catalog(self): return Catalog(self.root)
    def change_yaml(self, kind, fn):
        path=self.root/assetlib.KINDS[kind]; items=yaml_load(path.read_text());fn(items)
        path.write_text(yaml.safe_dump(items,allow_unicode=True,sort_keys=False))
    def change_registry(self, fn):
        path=self.root/'03_agent/skill_registry.json';data=json.loads(path.read_text());fn(data)
        path.write_bytes(canonical(data))
    def valid_report(self):
        c=self.catalog()
        return dict(schema_version='1.0',run_id='synthetic-unit-test',host='fixture',model='not-a-model',
                    reviewer='test',commit='a'*40,asset_digest=c.identity(),dataset_digest=assets.dataset_digest(c),
                    results=[dict(id=r['id'],answer='Synthetic fixture only',retrieved_refs=['XP-T-001'],
                                  scores={d:4 for d in assetlib.DIMENSIONS},fatal_violations=[],
                                  scoring_note='Synthetic data; not a behavior evaluation') for r in c.evals])


class ValidationTests(Base):
    def test_valid_assets(self):
        c=self.catalog();self.assertEqual(len(c.skills),7);self.assertEqual(len(c.evals),2)
        self.assertTrue(c.warnings)
    def test_yaml_duplicate_keys(self):
        with self.assertRaises(AssetError): yaml_load('a: 1\na: 2\n')
    def test_json_duplicate_keys(self):
        with self.assertRaises(AssetError): assetlib.json_load('{"x":1,"x":2}')
    def test_json_nan(self):
        with self.assertRaises(AssetError): assetlib.json_load('{"x":NaN}')
    def test_malformed_yaml(self):
        put(self.root,assetlib.KINDS['principle'],'[ broken')
        with self.assertRaises(AssetError): self.catalog()
    def test_malformed_jsonl(self):
        put(self.root,'06_evals/evals.jsonl','{not json}\n')
        with self.assertRaises(AssetError): self.catalog()
    def test_missing_required_field(self):
        self.change_yaml('principle',lambda x:x[0].pop('statement'))
        with self.assertRaises(AssetError): self.catalog()
    def test_invalid_model_status(self):
        self.change_yaml('model',lambda x:x[0].update(status='partial'))
        with self.assertRaises(AssetError): self.catalog()
    def test_duplicate_knowledge_id(self):
        self.change_yaml('principle',lambda x:x.append(copy.deepcopy(x[0])))
        with self.assertRaises(AssetError): self.catalog()
    def test_unknown_source(self):
        self.change_yaml('case',lambda x:x[0].update(source_refs=['XP-T-999']))
        with self.assertRaises(AssetError): self.catalog()
    def test_mistyped_reference(self):
        self.change_yaml('case',lambda x:x[0].update(model_refs=['XP-CL-001']))
        with self.assertRaises(AssetError): self.catalog()
    def test_active_legacy_anchor_fails(self):
        self.change_yaml('case',lambda x:x[0].update(source_refs=['XP-T-001#P001']))
        with self.assertRaises(AssetError): self.catalog()
    def test_archived_legacy_anchor_not_active(self):
        self.change_yaml('case',lambda x:x[0].update(legacy_source_refs=['XP-T-001#P001']))
        self.catalog()
    def test_anchor_resolution(self):
        r=self.catalog().resolve('XP-T-004#P001-P003');self.assertEqual(r['end'],3)
    def test_missing_anchor(self):
        with self.assertRaises(AssetError): self.catalog().resolve('XP-T-004#P001-P004')
    def test_reversed_anchor(self):
        with self.assertRaises(AssetError): self.catalog().resolve('XP-T-004#P003-P001')
    def test_file_level_resolution(self):
        self.assertEqual(self.catalog().resolve('XP-T-001')['locator'],'file_only')
    def test_strict_evidence_fails(self):
        with self.assertRaises(AssetError): self.catalog().strict_evidence()
    def test_raw_lock_mismatch(self):
        put(self.root,'01_source/raw/XP-T-001_raw.txt','changed')
        with self.assertRaises(AssetError): self.catalog()
    def test_reviewed_lock_mismatch(self):
        put(self.root,'01_source/reviewed/XP-T-004_reviewed.txt','changed')
        with self.assertRaises(AssetError): self.catalog()
    def test_path_traversal(self):
        for p in ('../x','/tmp/x','a/../../x','.git/config','a\\b'):
            with self.subTest(path=p),self.assertRaises(AssetError): assetlib.safe_path(self.root,p)
    @unittest.skipUnless(SYMLINKS_AVAILABLE, 'symlink creation unavailable on this platform')
    def test_symlink_rejected(self):
        path=self.root/'02_knowledge/case_cards.yaml';path.unlink();path.symlink_to(self.root/'02_knowledge/principle_cards.yaml')
        with self.assertRaises(AssetError): self.catalog()
    def test_fake_frontmatter(self):
        put(self.root,'.agents/skills/career-planning/SKILL.md','name: career-planning\ndescription: false frontmatter')
        with self.assertRaises(AssetError): self.catalog()
    def test_missing_frontmatter_end(self):
        with self.assertRaises(AssetError): assetlib.frontmatter('---\nname: test\n')
    def test_skill_version_mismatch(self):
        self.change_registry(lambda d:d['skills'][0].update(version='9.0.0'))
        with self.assertRaises(AssetError): self.catalog()
    def test_unknown_skill_dependency(self):
        self.change_registry(lambda d:d['skills'][0].update(skill_refs=['unknown']))
        with self.assertRaises(AssetError): self.catalog()
    def test_dependency_cycle(self):
        self.change_registry(lambda d:d['skills'][0].update(skill_refs=[d['skills'][0]['name']]))
        with self.assertRaises(AssetError): self.catalog()
    def test_skill_body_citation_drift(self):
        self.change_registry(lambda d:d['skills'][6].update(source_refs=['XP-T-004']))
        with self.assertRaises(AssetError): self.catalog()
    def test_duplicate_eval_id(self):
        path=self.root/'06_evals/evals.jsonl';data=path.read_bytes();path.write_bytes(data+data)
        with self.assertRaises(AssetError): self.catalog()
    def test_unregistered_skill_rejected(self):
        put(self.root,'.agents/skills/unreviewed/SKILL.md','---\nname: unreviewed\n---\n')
        with self.assertRaises(AssetError): self.catalog()
    def test_development_skill_not_runtime(self):
        put(self.root,'.agents/skills/create-readme/SKILL.md','development only')
        c=self.catalog(); assets.build(c)
        self.assertFalse((self.root/'dist/runtime/.agents/skills/create-readme').exists())
class BuildTests(Base):
    def test_deterministic_build(self):
        c=self.catalog();assets.build(c);first=(self.root/'dist/runtime.zip').read_bytes()
        assets.build(c);self.assertEqual(first,(self.root/'dist/runtime.zip').read_bytes());assets.check_build(c)
    def test_runtime_excludes_private_inbox_and_expected(self):
        put(self.root,'05_user_private/profile.md','SECRET_USER_SENTINEL')
        put(self.root,'01_source/inbox/unreviewed.txt','SECRET_INBOX_SENTINEL')
        assets.build(self.catalog())
        with zipfile.ZipFile(self.root/'dist/runtime.zip') as z:
            data=b''.join(z.read(p) for p in z.namelist())
            for secret in (b'SECRET_USER_SENTINEL',b'SECRET_INBOX_SENTINEL',b'PRIVATE_EXPECTED_SENTINEL'):
                self.assertNotIn(secret,data)
            self.assertFalse(any(p.startswith('06_evals/') for p in z.namelist()))
    def test_public_release_blocked(self):
        with self.assertRaises(AssetError): assets.build(self.catalog(),public=True)
        self.assertFalse((self.root/'dist').exists())
    def test_changed_after_validation_rejected(self):
        c=self.catalog();put(self.root,'03_agent/METHOD_POLICY.md','changed')
        with self.assertRaises(AssetError):assets.build(c)
    def test_undeclared_resource_not_packaged(self):
        put(self.root,'.agents/skills/career-planning/assets/private.md','PRIVATE_RESOURCE_SENTINEL')
        assets.build(self.catalog())
        self.assertFalse((self.root/'dist/runtime/.agents/skills/career-planning/assets/private.md').exists())
    def test_missing_runtime_file_detected(self):
        c=self.catalog();assets.build(c);(self.root/'dist/runtime/AGENTS.md').unlink()
        with self.assertRaises(AssetError): assets.check_build(c)
    def test_extra_runtime_file_detected(self):
        c=self.catalog();assets.build(c);put(self.root,'dist/runtime/secret.txt','oops')
        with self.assertRaises(AssetError): assets.check_build(c)
    def test_stale_build_detected(self):
        assets.build(self.catalog());put(self.root,'03_agent/METHOD_POLICY.md','new policy')
        with self.assertRaises(AssetError): assets.check_build(self.catalog())
    @unittest.skipUnless(SYMLINKS_AVAILABLE, 'symlink creation unavailable on this platform')
    def test_symlink_dist_rejected(self):
        (self.root/'dist').symlink_to(self.root/'03_agent',target_is_directory=True)
        with self.assertRaises(AssetError): assets.build(self.catalog())
    def test_unrecovered_backup_rejected(self):
        (self.root/'.dist-backup').mkdir()
        with self.assertRaises(AssetError): assets.build(self.catalog())
    def test_tampered_zip_detected(self):
        c=self.catalog();assets.build(c)
        with zipfile.ZipFile(self.root/'dist/runtime.zip','w') as z:z.writestr('bad','bad')
        with self.assertRaises(AssetError): assets.check_build(c)
    def test_html_escaped(self):
        self.change_yaml('principle',lambda x:x[0].update(title='<script>alert(1)</script>'))
        assets.build(self.catalog());page=(self.root/'dist/review_dashboard.html').read_text()
        self.assertNotIn('<script>',page);self.assertIn('&lt;script&gt;',page)


class EvaluationTests(Base):
    def test_prepare_does_not_send_expected(self):
        assets.prepare(self.catalog());text=(self.root/'dist/eval-prompts.jsonl').read_text()
        self.assertNotIn('expected_behavior',text);self.assertNotIn('PRIVATE_EXPECTED',text)
    def test_complete_synthetic_report(self):
        path=dump(self.root,'report.json',self.valid_report())
        self.assertEqual(assets.grade(self.catalog(),path)['passed'],2)
    def test_partial_report_fails(self):
        report=self.valid_report();report['results'].pop()
        with self.assertRaises(AssetError): assets.grade(self.catalog(),dump(self.root,'r.json',report))
    def test_duplicate_results_fail(self):
        report=self.valid_report();report['results'][1]=report['results'][0]
        with self.assertRaises(AssetError): assets.grade(self.catalog(),dump(self.root,'r.json',report))
    def test_fatal_violation_fails(self):
        report=self.valid_report();report['results'][0]['fatal_violations']=['unapproved_external_action']
        with self.assertRaises(AssetError): assets.grade(self.catalog(),dump(self.root,'r.json',report))
    def test_boundary_score_gate(self):
        report=self.valid_report();report['results'][0]['scores']={d:5 for d in assetlib.DIMENSIONS}
        report['results'][0]['scores']['boundary_awareness']=3
        with self.assertRaises(AssetError): assets.grade(self.catalog(),dump(self.root,'r.json',report))
    def test_wrong_snapshot_fails(self):
        report=self.valid_report();report['asset_digest']='0'*64
        with self.assertRaises(AssetError): assets.grade(self.catalog(),dump(self.root,'r.json',report))
    def test_boolean_score_not_integer(self):
        report=self.valid_report();report['results'][0]['scores']['source_fidelity']=True
        with self.assertRaises(AssetError): assets.grade(self.catalog(),dump(self.root,'r.json',report))
    def test_nonexistent_citation_fails(self):
        report=self.valid_report();report['results'][0]['retrieved_refs']=['XP-T-999']
        with self.assertRaises(AssetError): assets.grade(self.catalog(),dump(self.root,'r.json',report))
class IntakeTests(Base):
    def test_missing_transcript_has_no_intake(self):
        with self.assertRaises(AssetError):intake.stage(self.root,title='课',transcript=self.root/'missing.txt')
        self.assertFalse((self.root/'01_source/inbox').exists())
    def test_duplicate_id_rejected_without_directory(self):
        before=(self.root/'01_source/manifest.csv').read_bytes()
        with self.assertRaises(AssetError):intake.stage(self.root,title='课',source_id='XP-T-001')
        self.assertEqual(before,(self.root/'01_source/manifest.csv').read_bytes())
    def test_success_and_unique_next_id(self):
        sid,p=intake.stage(self.root,title='新课');self.assertEqual(sid,'XP-T-005');self.assertTrue(p.is_dir())
        self.assertEqual(intake.stage(self.root,title='另一课')[0],'XP-T-006')
    def test_newline_metadata_roundtrip(self):
        title='标题\n第二行';sid,p=intake.stage(self.root,title=title)
        self.assertEqual(yaml_load((p/'metadata.yaml').read_text())['course']['title'],title)
        self.assertEqual(intake.load_manifest(self.root/'01_source/manifest.csv')[1][-1]['title'],title)
    def test_bad_manifest_preflight(self):
        put(self.root,'01_source/manifest.csv','source_id,title\n')
        with self.assertRaises(AssetError):intake.stage(self.root,title='课')
        self.assertFalse((self.root/'01_source/inbox').exists())
    def test_invalid_date_preflight(self):
        with self.assertRaises(ValueError):intake.stage(self.root,title='课',date='2026-02-31')
        self.assertFalse((self.root/'01_source/inbox').exists())
    def test_empty_title(self):
        with self.assertRaises(AssetError):intake.stage(self.root,title=' ')
    def test_unknown_rights(self):
        with self.assertRaises(AssetError):intake.stage(self.root,title='课',rights_status='assumed')
    def test_duplicate_content(self):
        path=put(self.root,'another.txt',(self.root/'01_source/raw/XP-T-001_raw.txt').read_bytes())
        with self.assertRaises(AssetError):intake.stage(self.root,title='重复',transcript=path)
    def test_binary_input_rejected(self):
        path=put(self.root,'file.pdf',b'PDF')
        with self.assertRaises(AssetError):intake.stage(self.root,title='课',transcript=path)
    def test_empty_transcript(self):
        path=put(self.root,'empty.txt','')
        with self.assertRaises(AssetError):intake.stage(self.root,title='课',transcript=path)
    def test_existing_lock_not_removed(self):
        path=put(self.root,'01_source/.ingestion.lock','busy')
        with self.assertRaises(AssetError):intake.stage(self.root,title='课')
        self.assertEqual(path.read_text(),'busy')
    def test_manifest_replace_failure_rolls_back(self):
        before=(self.root/'01_source/manifest.csv').read_bytes()
        with patch('scaffold_new_course.os.replace',side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):intake.stage(self.root,title='课')
        self.assertEqual(before,(self.root/'01_source/manifest.csv').read_bytes())
        self.assertFalse((self.root/'01_source/inbox/XP-T-005').exists())
        self.assertFalse((self.root/'01_source/.ingestion.lock').exists())
        self.assertTrue((intake.stage(self.root,title='重试')[1]).exists())
    def test_staged_source_cannot_be_cited(self):
        sid,_=intake.stage(self.root,title='暂存')
        with self.assertRaises(AssetError):self.catalog().resolve(sid)
    def test_staged_source_not_in_runtime_manifest(self):
        intake.stage(self.root,title='STAGED_SECRET_TITLE')
        assets.build(self.catalog())
        self.assertNotIn('STAGED_SECRET_TITLE',(self.root/'dist/runtime/01_source/manifest.csv').read_text())

if __name__=='__main__':unittest.main()
