"""The representation study must refuse exclusions and policy confounding."""
import importlib.util
import json
from pathlib import Path

import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location('header_study', Path(__file__).resolve().parents[1] /
    'research/tier8_v2/experiments/header_materialization_study.py')
study = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(study)


def fixture_plan(tmp_path, n=73):
    source = tmp_path / 'source.json'
    original = [{'id': str(i), 'evidence': {'table_1': 'metric ; 2020: 1'}} for i in range(n)]
    table = [['year', '2019'], ['metric', '1']]
    source.write_text(json.dumps([{'id': x['id'], 'table': table} for x in original]))
    candidate = [study.materialize(x, table) for x in original]
    jobs = []
    for label, packets in [('control', original), ('header', candidate)]:
        path = tmp_path / (label + '.jsonl')
        path.write_text(''.join(json.dumps(x) + '\n' for x in packets))
        jobs.append({'name': 'sas-' + label, 'command': ['python', 'runner', '--data', str(path),
            '--evaluation-source', str(source)]})
    plan = tmp_path / 'plan.json'
    plan.write_text(json.dumps({'kind': 'fitting_only_header_representation', 'jobs': jobs,
        'proofs': {'sas-control': {}, 'sas-header': {}}, 'input_sha256': {}}))
    return plan, tmp_path / 'result.json', tmp_path / 'header.jsonl'


class HeaderStudyAudit(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / '.local')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_refuses_case_exclusion_before_trace_loading(self):
        plan, out, _ = fixture_plan(self.directory, n=72)
        with patch('tier8_v2_method_analyze.load_condition', side_effect=AssertionError('Must reject before trace loading')):
            with self.assertRaisesRegex(ValueError, 'All fitting cases required'):
                study.analyze(plan, 'sas', out)
        self.assertFalse(out.exists())

    def test_refuses_candidate_source_mutation_before_trace_loading(self):
        plan, out, candidate = fixture_plan(self.directory)
        packets = study.rows(candidate)
        packets[0]['evidence']['table_1'] += ' ; invented: 999'
        candidate.write_text(''.join(json.dumps(x) + '\n' for x in packets))
        with patch('tier8_v2_method_analyze.load_condition', side_effect=AssertionError('Must reject before trace loading')):
            with self.assertRaisesRegex(ValueError, 'Representation intervention differs'):
                study.analyze(plan, 'sas', out)
        self.assertFalse(out.exists())

    def test_refuses_checkpoint_confound_after_trace_loading(self):
        plan, out, _ = fixture_plan(self.directory)
        def loaded(job, *args):
            manifest = {k: 'same' for k in ('evaluation_source_sha256', 'code_sha256', 'models',
                'task_policy', 'runtime', 'verifier_adapter')}
            manifest['adapter'] = 'different' if job['name'].endswith('header') else 'original'
            return manifest, [], {}
        with patch('tier8_v2_method_analyze.load_condition', side_effect=loaded):
            with self.assertRaisesRegex(ValueError, 'Unmatched frozen policy: adapter'):
                study.analyze(plan, 'sas', out)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
