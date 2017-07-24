"""
    The simplist tree structure:
                root
    left-child          right-child

    There is only one HHH in the tree, the root node.

    We use this simple example to check the correctness of our code.
"""
import logging
import math
import numpy as np
from rwcb_one_subtree import rwcb_one_subtree

def generate_traffic():
    lambda_lists = [12, 13]
    traffic_file = "traffic_3nodes.txt"

    results = []
    iters = 1000
    for curr_l in lambda_lists:
        s = np.random.poisson(curr_l, iters)
        results.append(s)

    new_results = [[k[i] for k in results] for i in range(iters)]
    with open(traffic_file, 'wb') as ff:
        for line in new_results:
            line = ','.join([str(k) for k in line]) + '\n'
            ff.write(line)
    return traffic_file

def vary_error(infile, leaf_level, threshold, p_zero, error, xi, logging_level):
    errors = np.arange(0.01, 0.9, 0.05)
    vmax, vmin = 1.0/errors[0], 1.0/errors[-1]
    vmax, vmin = math.log(vmax), math.log(vmin)

    reci_errors = np.linspace(vmin, vmax, 50)
    errors = [1.0/float(math.exp(i)) for i in reci_errors]

    for error in errors:
        rwcb_one_subtree(infile, leaf_level, threshold, p_zero, error, xi, logging_level)

def main():
    leaf_level = 1

    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.5
    xi = 3.0
    threshold = 20

    #--------------------------------------------------------------------------------#
    # One-time
    """
    #infile =  generate_traffic()
    infile = "traffic_3nodes.txt"

    #rwcb_one_subtree(infile, leaf_level, threshold, p_zero, error, xi, logging.DEBUG)
    vary_error(infile, leaf_level, threshold, p_zero, error, xi)
    """
    #--------------------------------------------------------------------------------#
    # Mutiple iterations
    iterations = 1000
    for i in range(iterations):
        infile = generate_traffic()
        vary_error(infile, leaf_level, threshold, p_zero, error, xi, logging.INFO)

if __name__ == "__main__":
    main()

