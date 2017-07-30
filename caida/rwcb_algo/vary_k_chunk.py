"""
    For each K (number of leaf_nodes), we have one set of lambdas.
    Plot time_interval, precision, recall vs K.
"""
import os
import sys
import time
import math
import logging
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from load_lambdas import load_lambdas
from generator import generator, generator_file, generator_chunk
from read_file import read_file
from offline_caida import createTree, findHHH

from parallel_rwcb import parallel_rwcb_algo

def run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level):
    # One realization under the above distribution.
    outfile = "tmp_vary_k.txt"
    iterations = 5000
    traffic = generator_chunk(leaf_lambdas, iterations)
    
    # Run RWCB algorithm.
    pts = parallel_rwcb_algo(leaf_level, threshold, p_zero, error, xi, S, logging_level)
    for leaf_nodes in traffic:
        flag = pts.run(leaf_nodes)
        if flag:
            results = pts.report(tHHH_nodes)
            return results
    error_msg = "Error: End of file error occurred."
    results = [error_msg]
    return results


def monte_carlo(leaf_level, iterations, num_of_threads):
    # Load synthetic trace parameters
    #leaf_level = 16
    infile = "../data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(leaf_level)

    # log file
    logfile = "results/tmp/vary_k_l{0}.txt".format(leaf_level)
    #LOG = logging.getLogger(__name__)
    #handler = logging.FileHandler(logfile)
    #handler.setLevel(logging.INFO)
    #LOG.addHandler(handler)

    leaf_lambdas = load_lambdas(infile)
    total = sum([k[1] for k in leaf_lambdas])
    threshold = total * 0.1
   
    # Find true universal set of HHHes
    root, tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    S = len(tHHH_nodes)
    line = "True HHHes: {0}".format(tHHH_nodes)
    print line
    combine_results = [line]

    
    # rw_cb algorithm specific parameters
    # :param threshold: HHH threshold
    # :param epsno: parameter in equation (31) or (32)
    # :param p_zero: initialize p_zero
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.5
    error = p_init * 0.1
    xi = 6.0

    #---------------------------------------------------#
    import multiprocessing
    
    def worker(i, chunk, queue, leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level):
        results = []
        for i in range(chunk):
            results += run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level)
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
    print combine_results
    # Write combined results to logfile
    with open(logfile, 'wb') as ff:
        for line in combine_results:
            ff.write(line+'\n')

    #LOG.removeHandler(handler)    


def main():
    for leaf_level in range(16, 7, -1):
        start_time = time.time()
        print "leaf_level = {0}".format(leaf_level)
        monte_carlo(leaf_level, 10, 10)
        end_time = time.time()
        print "Time elapsed: ", end_time - start_time

 
if __name__ == "__main__":
    main() 
