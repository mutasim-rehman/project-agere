import ast
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import tier8_v2_natural_run as runner
from tier8_v2_method_plan import financial_command


class NaturalResearch(unittest.TestCase):
    def test_frozen_model_inference_class_is_unchanged(self):
        def model_tree(name):
            tree = ast.parse((ROOT / 'scripts' / name).read_text())
            return ast.dump(next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Models'))
        self.assertEqual(model_tree('tier8_v2_run.py'), model_tree('tier8_v2_natural_run.py'))

    def test_generated_sas_command_passes_actual_arm_guards(self):
        command = financial_command('sas', 'public', 'source', 'out', 'adapter', None, 'weights', 52)
        class BeforeAdapterLoad(Exception):
            pass
        with patch.object(sys, 'argv', command[1:]), \
                patch.object(runner, 'natural_partition', return_value={}), \
                patch.object(runner, 'financial_source', return_value=Path('source')), \
                patch.object(runner, 'load_adapter', side_effect=BeforeAdapterLoad):
            with self.assertRaises(BeforeAdapterLoad):
                runner.main()
        invalid = [*command, '--verifier-model', '3b']
        with patch.object(sys, 'argv', invalid[1:]):
            with self.assertRaisesRegex(ValueError, 'SAS verification uses its own'):
                runner.main()

    def test_partition_rejects_split_and_id_changes_even_with_updated_file_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); data = root / 'public.jsonl'; source = root / 'source-train.json'
            selection = root / 'selection.json'
            def save(row):
                data.write_text(json.dumps(row) + '\n')
                selection.write_text(json.dumps({'partitions': {'model_selection': {
                    'public_file': str(data), 'sha256': hashlib.sha256(data.read_bytes()).hexdigest(),
                    'ids': ['A/2000/page_1.pdf-1'], 'n': 1}}}))
            # Temporary test paths are explicitly permitted only for this pure validator.
            with patch.object(runner, 'inside', side_effect=Path):
                save({'id': 'A/2000/page_1.pdf-1', 'split': 'train'})
                self.assertEqual(runner.natural_partition(data, source)['partition'], 'model_selection')
                save({'id': 'A/2000/page_1.pdf-1', 'split': 'development'})
                with self.assertRaises(ValueError):
                    runner.natural_partition(data, source)
                save({'id': 'A/2000/page_1.pdf-2', 'split': 'train'})
                with self.assertRaises(ValueError):
                    runner.natural_partition(data, source)


if __name__ == '__main__':
    unittest.main()
