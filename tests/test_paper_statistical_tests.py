"""Known values for the paper's paired-test battery."""
import math
import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/reporting'))
from paper_statistical_tests import (binom_two_sided_half, chi2_sf, cluster_block, holm,
                                     mcnemar_block, symmetry_tests)


class PaperStatistics(unittest.TestCase):
    def test_chi_square_tail_matches_critical_values(self):
        for x, df in [(3.841459, 1), (5.991465, 2), (7.814728, 3), (9.487729, 4)]:
            self.assertAlmostEqual(chi2_sf(x, df), 0.05, places=6)
        self.assertEqual(chi2_sf(0.0, 1), 1.0)

    def test_exact_mcnemar_floor_needs_six_discordant_pairs(self):
        self.assertEqual(binom_two_sided_half(0, 5), 0.0625)
        self.assertEqual(binom_two_sided_half(0, 6), 0.03125)
        self.assertEqual(binom_two_sided_half(0, 0), 1.0)

    def test_wald_variance_and_continuity_correction(self):
        r = mcnemar_block(5, 0, 160)
        self.assertAlmostEqual(r['se_wald'], math.sqrt(5 - 25 / 160) / 160)
        self.assertEqual(r['chi2'], 5.0)
        self.assertEqual(r['chi2_cc'], 16 / 5)

    def test_bowker_decomposes_primary_table(self):
        s = symmetry_tests(np.array([[5, 1, 72], [0, 2, 46], [0, 0, 34]]))
        self.assertEqual((s['bowker_q'], s['bowker_df']), (119.0, 3))
        self.assertEqual(s['stuart_maxwell_df'], 2)
        self.assertEqual(symmetry_tests(np.diag([5, 3, 152]))['stuart_maxwell_df'], 0)

    def test_durkalski_reduces_to_mcnemar_with_singleton_clusters(self):
        d = np.array([1, 1, 1, -1, 0, 0], dtype=float)
        r = cluster_block(d, [str(i) for i in range(len(d))])
        self.assertAlmostEqual(r['durkalski_chi2'], (3 - 1) ** 2 / 4)

    def test_durkalski_is_bounded_by_nonzero_clusters(self):
        d = np.array([1, 1, 1, 1, -1, 1, 0], dtype=float)
        r = cluster_block(d, ['a', 'a', 'b', 'c', 'c', 'd', 'e'])
        self.assertLessEqual(r['durkalski_chi2'], 4 + 1e-12)

    def test_holm_step_down(self):
        self.assertEqual(holm([.01, .04, .03]), [.03, .06, .06])


if __name__ == '__main__':
    unittest.main()
