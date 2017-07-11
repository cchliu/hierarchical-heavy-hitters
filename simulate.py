import numpy as np

import rw_cb

p_init = 1 - 1.0 / (2**(1.0/3.0))

scales = np.arange(0, 1.0, 0.1)
for scale in scales:
    error = p_init * scale
    rw_cb.setup_params_error(error)
    rw_cb.print_params()
    rw_cb.rw_cb_algo()
