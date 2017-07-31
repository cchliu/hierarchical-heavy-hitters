"""
    Assume there is only one HHH at position (leaf_level-1, 1).
    We vary K to plot the curve between sample complexity and K.

    :param K: The number of leaf nodes.
    :param leaf_level: The depth of the tree.
    :param threshold: HHH threshold in percentage of total traffic count.
"""
import math
import time
import logging
import numpy as np
import os
import sys
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from rwcb_multi_hhh import update_hhh_count
from read_file import read_file_old
from generator import generator_chunk
from rwcb_multi_statesman import rwcb_algo
from offline_caida import createTree, findHHH
from metric import precision, recall


def load_lambdas(leaf_level):
    """Generate traffic count per leaf node following Poisson distribution."""

    K = 2**leaf_level

    # Assume there is only one HHH at position (leaf_level-1, 1)
    leaf_left_child = 5 * 2**leaf_level
    leaf_right_child = 5 * 2**leaf_level

    leaf_lambdas = [1] * K
    leaf_lambdas[0] = leaf_left_child
    leaf_lambdas[1] = leaf_right_child

    leaf_lambdas = [[(leaf_level, idx+1), val] for idx, val in enumerate(leaf_lambdas)]
    return leaf_lambdas

def run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level):
    # :param time_interval: The index of current time interval.
    time_interval = 0

    # :param HHH_nodes: a list to store detected HHH's
    # key: (l, k), value: :class:`node_status' 
    HHH_nodes = {}

    # Instantiate one tree search object
    ts = rwcb_algo(threshold, p_zero, error, xi)
    ts.set_leaf_level(leaf_level)
    ts.init_start_node((0,1))
    ts.set_scale_const(S)
    ts.set_logging_level(logging_level)
    state = "state_one"

    iterations = 1000
    traffic = generator_chunk(leaf_lambdas, iterations)

    # Run RWCB algorithm.
    for leaf_nodes in traffic:
        if state == "break":
            # Calculate precision and recall
            rHHH_nodes = HHH_nodes
            p = precision(rHHH_nodes, tHHH_nodes)
            r = recall(rHHH_nodes, tHHH_nodes)
            line = "At leaf_level = {0}, error = {1}, xi = {2}, at time = {3}, stop the search. precision: {4}, recall: {5}".format(leaf_level, error, xi, time_interval, p, r)
            #print line
            return line

        time_interval += 1
        update_hhh_count(leaf_nodes, HHH_nodes)
        ts.set_time_interval(time_interval)
        state = ts.statesman(state, leaf_nodes, leaf_level, HHH_nodes)

    error_msg = "Not enough time intervals."
    return error_msg

def monte_carlo(leaf_lambdas, leaf_level, iterations, num_of_threads, threshold, p_zero, error, xi):
    # log file
    logfile = "results/tmp/sc_vs_k_l{0}.txt".format(leaf_level)
    S = 1
    tHHH_nodes = [(leaf_level-1, 1)]
    combine_results = []
    #---------------------------------------------------#
    import multiprocessing

    def worker(i, chunk, queue, leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level):
        results = []
        for i in range(chunk):
            line = run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level)
            results.append(line)
        queue.put(results)

    jobs = []
    result_queue = multiprocessing.Queue()
    chunk = int(math.ceil(iterations/num_of_threads))
    for i in range(num_of_threads):
        p = multiprocessing.Process(target=worker, args=(i, chunk, result_queue, leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging.WARNING,))
        jobs.append(p)
        p.start()

    for i in range(num_of_threads):
        combine_results += result_queue.get()

    for p in jobs:
        p.join()
    #---------------------------------------------------#
    # Write combined results to logfile
    with open(logfile, 'wb') as ff:
        for line in combine_results:
            ff.write(line+'\n')

def main():
    leaf_levels = np.arange(3, 11)

    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.5
    xi = 6.0
    iterations = 2000
    num_of_threads = 10

    for leaf_level in leaf_levels:
        print "leaf_level: ", leaf_level
        start_time = time.time()
        leaf_lambdas = load_lambdas(leaf_level)
        threshold = 7 * 2**leaf_level
        monte_carlo(leaf_lambdas, leaf_level, iterations, num_of_threads, threshold, p_zero, error, xi)
        end_time = time.time()
        print "Elapsed time: ", end_time - start_time


if __name__ == "__main__":
    main()

