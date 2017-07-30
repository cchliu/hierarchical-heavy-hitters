import sys
import logging
import math
import os,sys
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from rwcb_multi_hhh import update_hhh_count
from read_file import read_file_old
from generator import generator_chunk
from parallel_rwcb import parallel_rwcb_algo
from offline_caida import createTree, findHHH
from metric import precision, recall
#---------------------------------------------#
# logging
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#---------------------------------------------#
def run(leaf_level, leaf_lambdas, tHHH_nodes, threshold, p_zero, error, xi, S, logging_level):
    iterations = 5000
    traffic = generator_chunk(leaf_lambdas, iterations)

    # Run RWCB algorithm.
    pts = parallel_rwcb_algo(leaf_level, threshold, p_zero, error, xi, S, logging_level)
    for leaf_nodes in traffic:
        flag = pts.run(leaf_nodes)
        if flag:
            rHHH_nodes = pts.HHH_nodes.keys()
            print "reported HHHes: ", rHHH_nodes
            time_interval = pts.time_interval
            # Calculate precision and recall
            p = precision(rHHH_nodes, tHHH_nodes)
            r = recall(rHHH_nodes, tHHH_nodes)
            line = "At leaf_level = {0}, error = {1}, at time = {2}, stop the search. precision: {3}, recall: {4}".format(leaf_level, error, time_interval, p, r)
            print line 


def main():
    infile = "traffic_twoHHH.txt"
    infile = "traffic.txt"
    leaf_level = 3
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.1
    xi = 6.0
    threshold = 25

    #----------------------------------------#
    # Find true universal set of HHHes.
    #----------------------------------------#    
    leaf_lambdas = [[(3,1),20], [(3,2),10], [(3,3),1], [(3,4),1], [(3,5),1], [(3,6),1], [(3,7),1], [(3,8),1]]
    leaf_lambdas = [[(3,1),15], [(3,2),15], [(3,3),1], [(3,4),1], [(3,5),6], [(3,6),8], [(3,7),8], [(3,8),8]]

    root,tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    S = len(tHHH_nodes)
    print "Truee HHHes: ", tHHH_nodes

    for i in range(20):
        run(leaf_level, leaf_lambdas, tHHH_nodes, threshold, p_zero, error, xi, S, logging.WARNING)

if __name__ == "__main__":
    main()
