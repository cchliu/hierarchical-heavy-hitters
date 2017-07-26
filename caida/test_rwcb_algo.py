"""
    Test rw_cb algorithm.

    Read one instance of caida trace and use the values as leaf lambdas.
    Scale lambdas.
    Generate synthetic traces following Poisson distribution.

    Divid into subtrees.
    - :param S: Number of HHH nodes.
    - :param N: Number of counters.
    - N = num_of_TCAM = 2*S + 2, same as the settings in Yu's algorithm.
    - :param M: M = N-S
        - 2**l0 <= M < 2**(l0+1)
        - Subtrees with root node on level l0:
            - 2**l0 - (M-2**l0) = 2**(l0+1) - M
        - Subtrees with root node on level l1:
            - 2*(M - 2**l0) = 2M - 2**(l0+1)

    Search all subtrees to find HHHes at lower levels.

    After finishing searching all subtrees, start from the root node
    to search for HHH's on topper levels.
"""
import math
from generator import generator
from tree_operation import parent, left_child, right_child, sibling
from offline_caida import createTree, findHHH

from rwcb_multi_statesman import rwcb_algo
from rwcb_multi_read import read_file, update_hhh_count


def main():
    # Read one instance of caida trace. Use the value as the leaf lambdas.
    leaf_lambdas = []
    leaf_level = 16

    infile = "equinix-chicago.dirA.20160406-140200.UTC.anon.agg.csv"
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n').split(',')
            prefix, val = line[0], int(line[1])
            b1, b2 = [int(k) for k in prefix.split('.')]
            index = b1 * 256 + b2 + 1
            tag = (leaf_level, index)
            val = int(float(val) / 10000)
            leaf_lambdas.append([tag, val])
    total = sum([k[1] for k in leaf_lambdas])
    threshold = total * 0.1

    #----------------------------------------#
    # Find true universal set of HHHes.
    #----------------------------------------#    
    root,tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)

    #----------------------------------------------------#
    # rw_cb algorithm specific parameters
    # :param threshold: HHH threshold
    # :param epsno: parameter in equation (31) or (32)
    # :param p_zero: initialize p_zero
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.5
    xi = 6.0

    #----------------------------------------------------#
    # rw_cb algorithm global variables.
    # :param time_interval: The index of current time interval.
    time_interval = 0

    # :param HHH_nodes: a list to store detected HHH's
    # key: (l, k), value: :class:`node_status' 
    HHH_nodes = {}

    #----------------------------------------------------#
    """Divide into subtrees."""
    # :param N: The number of counters
    # :param S: The number of HHH's
    S  = 10
    N = 2*S + 2
    M = N - S
    # 2^l0 <= M < 2^(l0+1)
    l0 = int(math.log(M, 2))
    l1 = l0 + 1
    # :param n0: Number of subtrees with roots on level l0
    # :param n1: Number of subtrees with roots on level l1
    n1 = 2*(M - 2**l0)
    n0 = 2**(l1) - M

    # A list of subtree search objects
    # And its corresponding states
    subts, states = [], []
    for i in range(M):
        if i < n0:
            root_node = (l0, i+1)
        else:
            root_node = (l1, n0+i+1)

        # Instantiate subtree search object
        ts = rwcb_algo(threshold, p_zero, error, xi)
        ts.set_leaf_level(leaf_level)
        ts.init_start_node(root_node)
        ts.set_logging_level(logging.DEBUG)
        subts.append(ts)
        states.append("state_one")
    #-------------------------------------------------------# 
    num_of_subts = len(subts)
    next_subts, next_states = [], []
    while num_of_subts:
        # Not all subtrees finish searching.
        traffic = generator(leaf_lambdas)
        time_interval += 1
        update_hhh_count(traffic, leaf_level, HHH_nodes)
        for idx, ts in enumerate(subts):
            ts.set_time_interval(time_interval)
            state = states[idx]
            state = ts.statesman(state, line, leaf_level, HHH_nodes)
            if state == "break":
                num_of_subts -= 1
            else:
                next_subts.append(ts)
                next_states.append(state)

        subts = next_subts
        states = next_states
        next_subts, next_states = [], []
    #--------------------------------------------------------#
    # All subtrees finish searching.
    # Search HHH's in the top level. 
    root_node = (0, 1)
    ts = rwcb_algo(threshold, p_zero, error, xi)
    ts.set_leaf_level(leaf_level)
    ts.init_start_node(root_node)
    ts.set_logging_level(logging.DEBUG)
    state = "state_one"

    while True:
	traffic = generator(leaf_lambdas)
	time_interval += 1
	update_hhh_count(traffic, leaf_level, HHH_nodes)
	ts.set_time_interval(time_interval)
	if state == "break":
	    break
	state = ts.statesman(state, line, leaf_level, HHH_nodes)

