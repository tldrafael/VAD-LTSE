
import ltsd_rafa as ltsd
import numpy as np
# test-1

ffts_list = []
ffts_list.append(np.array([8, 1, 1, 1, 1, 1, 1, 1, 8]))
ffts_list.append(np.array([1, 7, 1, 1, 1, 1, 1, 7, 1]))
ffts_list.append(np.array([1, 1, 6, 1, 1, 1, 6, 1, 1]))
ffts_list.append(np.array([1, 1, 1, 5, 1, 5, 1, 1, 1]))
ffts_list.append(np.array([1, 1, 1, 1, 4, 1, 1, 1, 1]))

n_bins = 8
n_order = 5

ltse_expected = [8, 7, 6, 5, 4, 5, 6, 7, 8]
ltse_simulated = ltsd.compute_ltse(ffts_list)
assert ltse_expected == ltse_simulated
