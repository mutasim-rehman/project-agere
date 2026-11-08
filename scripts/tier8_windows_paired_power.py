"""Prospective power sensitivity for a two-sided exact McNemar test."""
import json

import numpy as np
from scipy.stats import binom


def power(n, gain, loss):
    # First integrate the number of discordant pairs; conditional on it,
    # a discordance is a gain with probability gain / (gain + loss).
    probability_discordant = gain + loss
    discordances = np.arange(1, n + 1)
    cutoffs = binom.ppf(0.025, discordances, 0.5).astype(int)
    cutoffs -= binom.cdf(cutoffs, discordances, 0.5) > 0.025
    lower = binom.cdf(cutoffs, discordances, gain / probability_discordant)
    upper = binom.sf(discordances - cutoffs - 1, discordances, gain / probability_discordant)
    return float(np.sum(binom.pmf(discordances, n, probability_discordant) * (lower + upper)))


if __name__ == "__main__":
    result = []
    for gain, loss in ((3 / 16, 0), (0.15, 0.05), (0.125, 0.025), (0.10, 0.05)):
        required = next(n for n in range(4, 1501) if power(n, gain, loss) >= 0.80)
        result.append(dict(gain_probability=gain, loss_probability=loss,
                           power_n21=power(21, gain, loss), power_n40=power(40, gain, loss),
                           smallest_n_80_percent=required))
    print(json.dumps(result, indent=2))
