"""
    Assume there is only one HHH in the tree.

    We use one set of lambdas for leaf nodes, but generate
    multiple runs of traffic count.

    We vary error to get relationship between sample complexity and error.

    :param leaf_level: The depth of the tree.
    :param threshold: HHH threshold in percentage of total traffic count.
"""
import numpy as np
import math
from generator import generate_traffic
from rwcb_one_subtree import rwcb_one_subtree

def main():
    leaf_level = 3

    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.5
    xi = 3.0
    threshold = 25
    
    errors = np.arange(0.01, 0.9, 0.05)
    vmax, vmin = 1.0/errors[0], 1.0/errors[-1]
    vmax, vmin = math.log(vmax), math.log(vmin)
    
    reci_errors = np.linspace(vmin, vmax, 20)
    errors = [1.0/float(math.exp(i)) for i in reci_errors]
    
    iters = 10000
    for iteration in range(iters):
        infile = generate_traffic()
        for error in errors:
            rwcb_one_subtree(infile, leaf_level, threshold, p_zero, error, xi)


if __name__ == "__main__":
    main()

