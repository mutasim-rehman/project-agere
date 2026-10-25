from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from shared_role_models import activate_policy


class ActivationTests(unittest.TestCase):
    def runtime(self, fail=False):
        events, active = [], []
        model = SimpleNamespace(_ctx=SimpleNamespace(ctx='context'), n_tokens=123)
        def reset():
            events.append('reset')
            model.n_tokens = 0
        def clear(ctx):
            self.assertEqual(ctx, 'context')
            events.append('clear')
            active.clear()
        def set_adapter(ctx, handle, scale):
            self.assertEqual(model.n_tokens, 0)
            self.assertEqual(active, [])
            self.assertEqual(scale, 1.0)
            events.append(('set', handle))
            active.append(handle)
            return -1 if fail else 0
        model.reset = reset
        api = SimpleNamespace(llama_clear_adapter_lora=clear, llama_set_adapter_lora=set_adapter)
        return model, api, events, active

    def test_repeated_role_changes_never_accumulate_policies_or_kv(self):
        model, api, events, active = self.runtime()
        for role in ('actor', 'critic', 'actor'):
            model.n_tokens = 89
            activate_policy(model, api, role)
            self.assertEqual(active, [role])
            self.assertEqual(model.n_tokens, 0)
        self.assertEqual(events, ['reset', 'clear', ('set', 'actor'), 'reset', 'clear', ('set', 'critic'),
                                  'reset', 'clear', ('set', 'actor')])

    def test_native_failure_leaves_no_adapter_or_fallback(self):
        model, api, events, active = self.runtime(fail=True)
        with self.assertRaisesRegex(RuntimeError, 'no base-policy fallback'):
            activate_policy(model, api, 'critic')
        self.assertEqual(active, [])
        self.assertEqual(model.n_tokens, 0)
        self.assertEqual(events[-2:], ['clear', 'reset'])

    def test_missing_handle_does_not_change_live_state(self):
        model, api, events, active = self.runtime()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            activate_policy(model, api, None)
        self.assertEqual(events, [])


if __name__ == '__main__':
    unittest.main()
