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
    outfile = "tmp_vary_epsilon_{0}.txt".format(S)
    iterations = 1000
    generator_file(leaf_lambdas, iterations, outfile)
    
    # Run RWCB algorithm.
    ff = open(outfile, 'rb')
    pts = parallel_rwcb_algo(leaf_level, threshold, p_zero, error, xi, S, logging_level)
    while True:
        try:
            line = read_file(ff, leaf_lambdas)
            flag = pts.run(line)
            if flag:
                pts.report(tHHH_nodes)
                break
        except EOFError:
            print "Error: End of file error occurred."
            break

    # Close file
    ff.close()

def vary_error(leaf_level, error, iterations):
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
    print "No. of HHHes: {0}".format(S)

    # rw_cb algorithm specific parameters
    # :param threshold: HHH threshold
    # :param epsno: parameter in equation (31) or (32)
    # :param p_zero: initialize p_zero
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    #error = p_init * 0.5
    xi = 6.0

    for i in range(iterations):
        run(leaf_lambdas, leaf_level, tHHH_nodes, threshold, p_zero, error, xi, S, logging.WARNING)


def main():
    import math
    import numpy as np

    errors = np.arange(0.01, 0.9, 0.05)
    vmax, vmin = 1.0/errors[0], 1.0/errors[-1]
    vmax, vmin = math.log(vmax), math.log(vmin)

    reci_errors = np.linspace(vmin, vmax, 20)
    errors = [1.0/float(math.exp(i)) for i in reci_errors]

    leaf_level = 16
    iterations = 1000
    for error in errors:
        vary_error(leaf_level, error, iterations) 

 
if __name__ == "__main__":
    main() 
