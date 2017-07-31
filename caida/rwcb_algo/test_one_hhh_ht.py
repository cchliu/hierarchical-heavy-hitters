import sys
import logging
import math
import os,sys
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from rwcb_multi_hhh import update_hhh_count
from read_file import read_file_old
from generator import generator_chunk, generator_chunk_ht, generator_ht
from rwcb_multi_statesman_ht import rwcb_algo
from offline_caida import createTree, findHHH
#---------------------------------------------#
# logging
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#---------------------------------------------#

def rwcb_one_subtree(leaf_lambdas, leaf_level, threshold, p_zero, error, b, u, logging_level):
    # :param time_interval: The index of current time interval.
    time_interval = 0
    
    # :param threshold: HHH threshold
    # :param b: parameter in equation (31) or (32)
    # :param u: parameter in equation (31) or (32)
    # :param p_zero: initialize p_zero

    # Parameters about the tree
    # :param leaf_level: The depth of the tree.
    #leaf_level = 3

    # :param HHH_nodes: a list to store detected HHH's
    # key: (l, k), value: :class:`node_status' 
    HHH_nodes = {}
    
    # Instantiate one tree search object
    ts = rwcb_algo(threshold, p_zero, error, b, u)
    ts.set_leaf_level(leaf_level)
    ts.init_start_node((0,1))
    ts.set_scale_const(1)
    ts.set_logging_level(logging_level)
    state = "state_one" 

    iterations = 10000
    #traffic = generator_chunk_ht(leaf_lambdas, iterations)

    #for line in traffic:
    #    print [k[1] for k in line]
    # Run RWCB algorithm.
    #for leaf_nodes in traffic:
    while True:
        leaf_nodes = generator_ht(leaf_lambdas)
        if state == "break":
            LOG.info("error = {0}, time_interval: {1}".format(error, time_interval))
            return
        time_interval += 1
        update_hhh_count(leaf_nodes, HHH_nodes)
        ts.set_time_interval(time_interval)
        state = ts.statesman(state, leaf_nodes, leaf_level, HHH_nodes)
    LOG.info("Not enough time intervals.")

def get_param_u(leaf_lambdas):
    sigmas = [math.sqrt(2*math.log(k[1])) for k in leaf_lambdas]
    return max(sigmas)

def main():
    infile = "traffic_twoHHH.txt"
    infile = "traffic.txt"
    leaf_level = 3
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.5
    error = p_init * 0.1
    b = 2
    threshold = 25

    leaf_lambdas = [[(3,1),20], [(3,2),10], [(3,3),1], [(3,4),1], [(3,5),1], [(3,6),1], [(3,7),1], [(3,8),1]]
    max_sigma = get_param_u(leaf_lambdas)
    u = math.exp(max_sigma**2)
    u = 100.0

    root,tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    print "Truee HHHes: ", tHHH_nodes

    for i in range(1):
        rwcb_one_subtree(leaf_lambdas, leaf_level, threshold, p_zero, error, b, u, logging.DEBUG)


if __name__ == "__main__":
    main()
