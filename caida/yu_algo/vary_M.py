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
import math
import logging
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from load_lambdas import load_lambdas
from generator import generator, generator_file
from read_file import read_file
from offline_caida import createTree, findHHH

from yu_algo import yu_algo

def write2file(results, logfile, mode):
    with open(logfile, mode) as ff:
        for line in results:
            ff.write(line)

def run(outfile, M, leaf_lambdas, S, threshold, leaf_level, tHHH_nodes, logfile):
    # Run minlan's algorithm.
    ff = open(outfile, 'rb')
    hs = yu_algo(S, threshold, leaf_level)
    
    results = []
    while True:
        try:
            leaf_nodes = [[k[0], 0] for k in leaf_lambdas]
            for i in range(M):
                line = read_file(ff, leaf_lambdas)
                for j in range(len(line)):
                    leaf_nodes[j][1] += line[j][1]
            leaf_nodes = [[k[0], k[1]/float(M)] for k in leaf_nodes]
            hs.add_time_interval(M)
            hs.run(leaf_nodes)
            results += hs.report(tHHH_nodes)
            if len(results) % 100 == 0:
                write2file(results, logfile, 'ab')
                results = []
        except EOFError:
            print "Error: End of file error occurred."
            break

    # Close file
    ff.close()

def vary_M(leaf_level):
    # Load synthetic trace parameters
    #leaf_level = 16
    infile = "../data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(leaf_level)
    leaf_lambdas = load_lambdas(infile)

    total = sum([k[1] for k in leaf_lambdas])
    threshold = total * 0.1
    S = 10

    # Find true universal set of HHHes
    root, tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    print "True HHHes: ", tHHH_nodes

    # One realization under the above distribution.
    outfile = "tmp.txt"
    iterations = 50000
    generator_file(leaf_lambdas, iterations, outfile)

    for M in [10, 20, 50]:
        logfile = "results/vary_M{0}.txt".format(M)
        line = "True HHHes: {0}\n".format(tHHH_nodes)
        with open(logfile, 'wb') as ff:
            ff.write(line)
        run(outfile, M, leaf_lambdas, S, threshold, leaf_level, tHHH_nodes, logfile)

def main():
    leaf_level = 16
    vary_M(leaf_level)

if __name__ == "__main__":
    main()
