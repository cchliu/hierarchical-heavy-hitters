"""
    Assume there is only one HHH at position (leaf_level-1, 1).
    We vary K to plot the curve between sample complexity and K.

    :param K: The number of leaf nodes.
    :param leaf_level: The depth of the tree.
    :param threshold: HHH threshold in percentage of total traffic count.
"""
import numpy as np
from rwcb_one_subtree import rwcb_one_subtree

def generate_traffic(leaf_level):
    """Generate traffic count per leaf node following Poisson distribution."""

    K = 2**leaf_level

    # Assume there is only one HHH at position (leaf_level-1, 1)
    leaf_left_child = 5 * 2**leaf_level
    leaf_right_child = 5 * 2**leaf_level

    lambda_lists = [1] * K
    lambda_lists[0] = leaf_left_child
    lambda_lists[1] = leaf_right_child

    traffic_file = "traffic_tmp.txt"

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

def main():
    leaf_levels = np.arange(3, 20)

    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.5
    xi = 6.0
    #threshold = 25

    #infile = "traffic_twoHHH.txt"
    #rwcb_one_subtree(infile, 3, threshold, p_zero, error, xi)
    for leaf_level in leaf_levels:
        traffic_file = generate_traffic(leaf_level)
        threshold = 7 * 2**leaf_level
        rwcb_one_subtree(traffic_file, leaf_level, threshold, p_zero, error, xi)


if __name__ == "__main__":
    main()

