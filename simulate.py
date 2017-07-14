import numpy as np

#import rw_cb
import rw_cb_multi as rw_cb
#import rw_cb_wrong_v1 as rw_cb

p_init = 1 - 1.0 / (2**(1.0/3.0))

scales = np.arange(0.01, 1.0, 0.1)
for scale in scales:
    error = p_init * scale
    rw_cb.setup_params_error(error)
    p_zero = p_init * 0.3
    rw_cb.setup_params_pzero(p_zero)
    xi = 6.0
    rw_cb.setup_params_xi(xi)
    rw_cb.print_params()
    rw_cb.rw_cb_algo()
