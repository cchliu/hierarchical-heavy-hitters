import logging
import math
import collections
import time

from module.generator import generate_traffic
from module.offline_caida import load_lambdas, findHHH
from module.metric import precision, recall
from module.helper import get_constant

from tree_operations import read_hhh_nodes, construct
from multi_target_poisson import Pointer_Poisson

def loop_inner(L, infile, iters):
    # Logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # leaves: A dictionary with key = (l,k), value = lambda
    leaves = load_lambdas(infile)
    # Preprocess lambda range
    for k in leaves:
        leaves[k] /= 1000 if leaves[k]>1000 else 1
    total_count = sum([leaves[k] for k in leaves])

    # Find set of true HHHes based on leaf-node lambdas.
    ratio = 0.05
    eta = total_count * ratio
    hhh_nodes = findHHH(leaves, eta)
    Smax = len(hhh_nodes)
    tHHH = [(node.l, node.k) for node in hhh_nodes]
    tHHH = sorted(tHHH, key = lambda x:x[0], reverse=True)

    tHHH_vals = [((node.l, node.k), node.val) for node in hhh_nodes]
    tHHH_vals = sorted(tHHH_vals, key = lambda x:x[0][0], reverse=True)
    #logger.info("True HHHes: %s", \
    #        ','.join(str(k) for k in tHHH))

    # Run Algorithms.
    sorted_leaf_tags = sorted(leaves.keys(), key = lambda x:x[1])
    lambda_lists = [leaves[k] for k in sorted_leaf_tags]

    for i in range(iters):
        # Generate one realization of traffic under Poisson distribution
        # leaf node lambdas are set as above.
        generate_traffic(lambda_lists, 1000)

        """ RWCB ALGO API """
        # Parameters
        p_max = 1.0 - 1.0/float(2**(1.0/3))
        p0 = 0.9*p_max
        error, xi = 0.4, 1.0
        error_0 = error/float(2.0*Smax)

        # Instantiate a pointer
        scale = 3.0*L*get_constant(p0)
        #scale = 1.0
        l, k = 0, 0
        pntr = Pointer_Poisson(l, k, L, p0, eta, error_0, scale, logging.DEBUG, 0, xi)
        time_interval = 0

        # Keep monitoring detected HHH nodes
        # key: (l,k), val: newNode object
        HHH_nodes = {}
        infile = "traffic_tmp.txt"

        with open(infile, 'rb') as ff:
            for line in ff:
                time_interval += 1
                values = [int(k) for k in line.split(',')]
                dvalues = construct(values, sorted_leaf_tags)

                # Keep monitoring detected HHH nodes
                read_hhh_nodes(dvalues, HHH_nodes)
                hhh_node = pntr.run(dvalues, HHH_nodes)
                # If found a new HHH node, add it to the HHH_nodes set.
                if hhh_node:
                    HHH_nodes[(hhh_node.l, hhh_node.k)] = hhh_node
                    print HHH_nodes
                if not pntr.isActive():
                    break
        print "Time interval: %d" % time_interval

        # Calculating metrics
        mHHH = sorted(HHH_nodes.keys(), key = lambda x:x[0], reverse=True)
        mHHH_vals = [(k, HHH_nodes[k].x_mean_net) for k in HHH_nodes]
        mHHH_vals = sorted(mHHH_vals, key = lambda x:x[0][0], reverse=True)
        print "True HHHes: ", tHHH_vals 
        print "Measured HHHes: ", mHHH_vals

        p, r = precision(mHHH, tHHH), recall(mHHH, tHHH)
        print "Iter {0}, Level {1}: Time interval {2}, Precision {3}, Recall {4}".format(i, L, time_interval, p, r)


def loop_outer():
    # Different set of lambdas
    iters = 1
    for L in range(9, 10):
        infile = "caida_data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(L)
        loop_inner(L, infile, iters)

if __name__ == "__main__":
    loop_outer()

