"""
    For each K (number of leaf_nodes), we have one set of lambdas.
    Plot time_interval, precision, recall vs K.
"""
import os
import sys
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
    generator_file(leaf_lambdas, iterations, outfile)
    
    # Run RWCB algorithm.
    ff = open(outfile, 'rb')
    pts = parallel_rwcb_algo(leaf_level, threshold, p_zero, error, xi, S, logging_level)
    while True:
        try:
            line = read_file(ff, leaf_lambdas)
            flag = pts.run(line)
            if flag:
                results = pts.report(tHHH_nodes)
                break
        except EOFError:
            print "Error: End of file error occurred."
            error_msg = "Error: End of file error occurred"
            results = [error_msg]
            break

    # Close file
    ff.close()
    return results

def monte_carlo(leaf_level, iterations):
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
    print "True HHHes: {0}".format(tHHH_nodes)
    
    # rw_cb algorithm specific parameters
    # :param threshold: HHH threshold
    # :param epsno: parameter in equation (31) or (32)
    # :param p_zero: initialize p_zero
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.5
    error = 0.1
    xi = 6.0

    for i in range(iterations): 
        results = run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging.WARNING)
        print results
    #LOG.removeHandler(handler)    


def main():
    for leaf_level in range(16, 7, -1):
        print "leaf_level = {0}".format(leaf_level)
        monte_carlo(leaf_level, 1)

 
if __name__ == "__main__":
    main() 
