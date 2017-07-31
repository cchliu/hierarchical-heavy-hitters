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
from metric import precision, recall
from parallel_rwcb import parallel_rwcb_algo

def run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level):
    # One realization under the above distribution.
    iterations = 2000
    #traffic = generator_chunk(leaf_lambdas, iterations)
    
    # Run RWCB algorithm.
    pts = parallel_rwcb_algo(leaf_level, threshold, p_zero, error, xi, S, logging_level)
    #for leaf_nodes in traffic:
    while True:
        leaf_nodes = generator(leaf_lambdas)
        flag = pts.run(leaf_nodes)
        if flag:
            rHHH_nodes = pts.HHH_nodes.keys()
            #print "reported HHHes: ", rHHH_nodes
            time_interval = pts.time_interval
            # Calculate precision and recall
            p = precision(rHHH_nodes, tHHH_nodes)
            r = recall(rHHH_nodes, tHHH_nodes)
            line = "At leaf_level = {0}, error = {1}, xi = {2}, at time = {3}, stop the search. precision: {4}, recall: {5}".format(leaf_level, error, xi, time_interval, p, r)
            return line

    error_msg = "Error: End of file error occurred."
    return error_msg

def monte_carlo(leaf_level, iterations, threshold, p_zero, error, xi):
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
    sorted_leaf_lambdas = sorted(leaf_lambdas, key = lambda x:x[1], reverse=True)
    print sorted_leaf_lambdas[:50]
    total = sum([k[1] for k in leaf_lambdas])
    #threshold = total * 0.1

    # Find true universal set of HHHes
    root, tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    S = len(tHHH_nodes)
    
    results = [] 
    line = "True HHHes: {0}, {1}".format(S, tHHH_nodes)
    results.append(line)
    for i in range(iterations):
        line = run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging.WARNING)
        results.append(line)
   
    # Write combined results to logfile
    with open(logfile, 'wb') as ff:
        for line in results:
            ff.write(line+'\n')
 
     
def main(): 
    #-------------------------------------------------#
    # :param leaf_level: Leaf level = log(K), K is number of leaf nodes
    # :param threshold: HHH threshold
    # :param xi: parameter in equation (31) or (32)
    # :param p_zero: initialize p_zero
    # :param error: Error
    # :param iterations: Num of monte carlo runs
    leaf_level = 12
    threshold = 200
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = 0.1
    xi = 48.0
    iterations = 200

    start_time = time.time()
    print "leaf_level = {0}".format(leaf_level)
    monte_carlo(leaf_level, iterations, threshold, p_zero, error, xi)
    end_time = time.time()
    print "Time elapsed: ", end_time - start_time
    

if __name__ == "__main__":
    main() 
