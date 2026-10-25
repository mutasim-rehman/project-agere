"""Small metadata fixtures for native proof replay, not model/effect tests."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from tier8_v2_method_analyze import ArtifactChecks
from tier8_v2_last_logit_proof import label_logprobs
from binary_verifier_score import PREFIX


class NativeAudit(unittest.TestCase):
    def fixture(self, root):
        data = root / 'data.jsonl'; prompt = 'validation prompt'
        data.write_text(json.dumps({'source_id': 'v1', 'split': 'validation', 'prompt': prompt}) + '\n')
        digest = hashlib.sha256(data.read_bytes()).hexdigest()
        train = root / 'train'; train.mkdir()
        (train / 'manifest.json').write_text(json.dumps({'input_sha256': {str(data): digest}}))
        info = {'training_run': str(train)}
        phases = []
        for scale in (0., 1., 0.):
            logits = {'PASS': scale, 'FAIL': -.5, 'UNKNOWN': -1.}
            phases.append({'scale': scale, 'conditional_label_logprobs': label_logprobs(logits),
                'event': {'status': 'scored', 'label_logits': logits, 'prompt_tokens': 5,
                    'prompt': prompt, 'forced_prefix': PREFIX,
                    'prompt_sha256': hashlib.sha256((prompt + PREFIX).encode()).hexdigest()}})
        effect = max(abs(phases[0]['conditional_label_logprobs'][k] - phases[1]['conditional_label_logprobs'][k])
                     for k in phases[0]['conditional_label_logprobs'])
        proof = {'pass': True, 'adapter': info, 'phases': phases, 'logits_all': False,
            'native_entry_points_equal': True, 'actual_generated_tokens': 0, 'actual_prefill_tokens': 15,
            'zero_repeat_max_label_logprob_drift': 0., 'max_label_logprob_effect': effect,
            'verified_models': [], 'dataset': str(data), 'dataset_sha256': digest, 'source_id': 'v1'}
        (root / 'manifest.json').write_text(json.dumps({'cap_bytes': 6400000000,
            'source_sha256': {}, 'dataset_sha256': digest}))
        (root / 'summary.json').write_text(json.dumps({'status': 'complete', 'exit_code': 0,
            'peak_tree_rss_bytes': 1000, 'cap_bytes': 6400000000, 'memory_breach': False}))
        return info, proof

    def test_native_proof_uses_actual_normalizer_and_prefixed_prompt_hash(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.local/tmp') as temp:
            root = Path(temp); info, proof = self.fixture(root)
            (root / 'proof.json').write_text(json.dumps(proof))
            ArtifactChecks().proof(info, root, [])
            proof['phases'][0]['event']['prompt_sha256'] = hashlib.sha256(b'validation prompt').hexdigest()
            (root / 'proof.json').write_text(json.dumps(proof))
            with self.assertRaisesRegex(ValueError, 'Proof prompt differs'):
                ArtifactChecks().proof(info, root, [])

    def test_native_proof_rejects_changed_prefix_and_effect_report(self):
        with tempfile.TemporaryDirectory(dir=ROOT / '.local/tmp') as temp:
            root = Path(temp); info, proof = self.fixture(root)
            for kind in ('prefix', 'effect'):
                bad = deepcopy(proof)
                if kind == 'prefix':
                    bad['phases'][0]['event']['forced_prefix'] = ''
                else:
                    bad['max_label_logprob_effect'] += .5
                (root / 'proof.json').write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    ArtifactChecks().proof(info, root, [])


if __name__ == '__main__':
    unittest.main()
