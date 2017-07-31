"""
    Test yu's algorithm.
    - Will precision and recall converge?

    Read one instance of caida trace and use the values as leaf lambdas.
    Scale lambdas.
    Generate synthetic traces following Poisson distribution.

    - Run offline algorithm to report true HHHes within this time interval.
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

from yu_algo import yu_algo

def write2file(results, logfile, mode):
    with open(logfile, mode) as ff:
        for line in results:
            ff.write(line)

def chunks(data, M):
    """ Divides the data into M  rows each """
    for i in xrange(0, len(data), M):
        yield data[i:i+M]

def run(leaf_level, leaf_lambdas, M, threshold, S, tHHH_nodes):
    # One realization under the above distribution.
    iterations = 50000
    traffic = generator_chunk(leaf_lambdas, iterations)

    # Run minlan's algorithm.
    hs = yu_algo(S, threshold, leaf_level)
    results = []

    divTrace = chunks(traffic, M)
    for chunk in divTrace:
        lenth = len(chunk)
        leaf_nodes = [[k[0], 0] for k in leaf_lambdas]
        for row in chunk:
            for j in range(len(row)):
                leaf_nodes[j][1] += row[j][1]
        leaf_nodes = [[k[0], k[1]/lenth] for k in leaf_nodes]
        hs.add_time_interval(lenth)
        hs.run(leaf_nodes)
        
        # Calcualte precision and recall
        rHHH_nodes = hs.rHHH_nodes
        line = "Reported HHHes: {0}".format(rHHH_nodes)
        results.append(line)
        time_interval = hs.time_interval
        p = precision(rHHH_nodes, tHHH_nodes)
        r = recall(rHHH_nodes, tHHH_nodes)
        line = "At leaf_level = {0}, At time interval = {1}, precision: {2}, recall: {3}".format(leaf_level, time_interval, p, r)
        results.append(line)
    return results


def monte_carlo(leaf_level, iterations, num_of_threads, M, threshold):
    # Load synthetic trace parameters
    #leaf_level = 16
    infile = "../data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(leaf_level)
    leaf_lambdas = load_lambdas(infile)

    logfile = "results/tmp/vary_k_l{0}.txt"
    #total = sum([k[1] for k in leaf_lambdas])
    #threshold = total * 0.1

    # Find true universal set of HHHes
    root, tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    S = len(tHHH_nodes)
    print "True HHHes: {0}, {1}".format(S, tHHH_nodes)

    """
    for i in range(iterations):
        logfile_iter = "results/tmp/vary_k_l{0}_M{1}_iter_{2}.txt".format(leaf_level, M, i)
        results = []
        line = "True HHHes: {0}, {1}".format(S, tHHH_nodes)
        results.append(line)
        results += run(leaf_level, leaf_lambdas, M, threshold, S, tHHH_nodes)
        
        # Write to logfile_iter
        with open(logfile_iter, 'wb') as ff:
            for line in results:
                ff.write(line + '\n')
    """
    #---------------------------------------------------#
    import multiprocessing

    def worker(i, chunk, leaf_lambdas, leaf_level, M, threshold, S, tHHH_nodes):
        results = []
        for j in range(chunk):
            logfile_iter = "results/tmp/vary_k_l{0}_M{1}_iter_{2}.txt".format(leaf_level, M, i*chunk+j)
            results = []
            line = "True HHHes: {0}, {1}".format(S, tHHH_nodes)
            results.append(line)
            results += run(leaf_level, leaf_lambdas, M, threshold, S, tHHH_nodes)
            
            # Write to logfile_iter
            with open(logfile_iter, 'wb') as ff:
                for line in results:
                    ff.write(line + '\n')

    
    jobs = []
    chunk = int(math.ceil(iterations/num_of_threads))
    for i in range(num_of_threads):
        p = multiprocessing.Process(target=worker, args=(i, chunk, leaf_lambdas, leaf_level, M, threshold, S, tHHH_nodes,))
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()
    #---------------------------------------------------#

def main():
    #leaf_level = 8
    #threshold = total * 0.1
    threshold = 200
    M = 10
    iterations = 10
    num_of_threads = 5

    for leaf_level in range(12, 13):
        start_time = time.time()
        print "leaf_level = {0}".format(leaf_level)
        monte_carlo(leaf_level, iterations, num_of_threads, M, threshold)
        end_time = time.time()
        print "Time elapsed: ", end_time - start_time


if __name__ == "__main__":
    main()
