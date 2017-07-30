"""
    Fix K = 2**16, one set of lambdas.
    What kind of xi to choose?
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

from parallel_rwcb import parallel_rwcb_algo

def run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level):
    # One realization under the above distribution.
    outfile = "tmp.txt"
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
                print pts.report(tHHH_nodes)
                break
        except EOFError:
            print "Error: End of file error occurred."
            break

    # Close file
    ff.close()

def vary_xi(leaf_level):
    # Load synthetic trace parameters
    #leaf_level = 16
    infile = "../data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(leaf_level)
    leaf_lambdas = load_lambdas(infile)

    total = sum([k[1] for k in leaf_lambdas])
    threshold = total * 0.1
   
    # Find true universal set of HHHes
    root, tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    print "True HHHes: ", tHHH_nodes
    S = len(tHHH_nodes)

    # rw_cb algorithm specific parameters
    # :param threshold: HHH threshold
    # :param epsno: parameter in equation (31) or (32)
    # :param p_zero: initialize p_zero
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.5
    xi = 6.0

    for xi in [0.1, 1.0, 5.0, 10.0, 50.0, 100.0, 200.0]:
        print "xi = {0}".format(xi)
        run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging.WARNING)

def main():
    for leaf_level in range(16, 7, -1):
        print "leaf_level = {0}".format(leaf_level)
        vary_xi(leaf_level)

 
if __name__ == "__main__":
    main() 
