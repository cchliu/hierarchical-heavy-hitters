import logging
import time
import math

from module.generator import generate_traffic
from module.offline_caida import load_lambdas, findHHH
from module.metric import precision, recall, error_function
from module.helper import get_constant

from parallel import run_one_instance

def loop_inner(L, infile, iterations):
    # leaves: A dictionary with key = (l,k), value = lambda
    leaves = load_lambdas(infile)
    for k in leaves:
        leaves[k] /= 1000 if leaves[k]>1000 else 1
        #leaves[k] /= 1000

    tmpFile = 'level{0}_lambdas.txt'.format(L)
    with open(tmpFile, 'wb') as ff:
        for (l,k) in sorted(leaves.keys(), key = lambda x:x[1]):
            line = ','.join([str(l), str(k), str(leaves[(l,k)])])
            ff.write(line + '\n')

    total_count = sum([leaves[k] for k in leaves])

    # Find set of true HHHes based on leaf-node lambdas.
    ratio = 0.05
    eta = total_count * ratio
    thhh_nodes = findHHH(leaves, eta)
    Smax = len(thhh_nodes)

    # Number of counters
    T = Smax*2+2
    tHHH = [(node.l, node.k) for node in thhh_nodes]

    # Run RWCB algo.
    sorted_leaf_tags = sorted(leaves.keys(), key = lambda x:x[1])
    lambda_lists = [leaves[k] for k in sorted_leaf_tags]

    name = 'Poisson'
    tmpFile = 'traffic_tmp_rwcb.txt'
    for i in range(iterations):
        # Generate one realization of traffic under Poisson distribution
        # leaf node lambdas are set as above.
        traffic_file = generate_traffic(lambda_lists, 1000, tmpFile)

        p_max = 1.0 - 1.0/float(2**(1.0/3))
        p0 = 0.9*p_max
        error, xi = 0.01, 1.0
        error_0 = error/float(2.0*Smax)

        max_scale = 3.0*L*get_constant(p0)
        max_scale /= float(64)
        #scaleList = [10**(k) for k in range(int(math.log(max_scale, 10)))] + [max_scale]
        scaleList = [max_scale]
        for scale in scaleList:
            # Run rwcb algo
            mhhh_nodes, time_interval = run_one_instance(traffic_file, L, sorted_leaf_tags, name, p0, eta, error_0, scale, logging.WARNING, T, xi)
            mHHH = sorted(mhhh_nodes.keys(), key = lambda x:x[0], reverse=True)
            #print "True HHHes: %s" % ', '.join([str((node.l, node.k))+':'+str(node.val) for node in thhh_nodes])
            #print "Reported HHHes: %s" %  ', '.join([str(k)+':'+str(mhhh_nodes[k].x_mean_net) for k in mHHH])
            p, r = precision(mHHH, tHHH), recall(mHHH, tHHH)
            o = error_function(mHHH, tHHH)
            print "Iter {0}, Level {1}, Ratio {2}, Error {3}, Scale {4}: Time interval {5}, Error_function {6}, Precision {7}, Recall {8}, Counter {9}".format(i, L, ratio, error, scale, time_interval, o, p, r, T)


def loop_outer():
    iters = 0
    for L in range(8, 9):
        infile = "caida_data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(L)
        loop_inner(L, infile, iters)

if __name__ == "__main__":
    loop_outer()

