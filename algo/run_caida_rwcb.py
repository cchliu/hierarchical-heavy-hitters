import logging
import time

from module.generator import generate_traffic
from module.offline_caida import load_lambdas, findHHH
from module.metric import precision, recall, error_function
from module.helper import get_constant

from parallel import run_one_instance

def loop_inner(L, infile, iterations, ratio):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # leaves: A dictionary with key = (l,k), value = lambda
    leaves = load_lambdas(infile)
    for k in leaves:
        #leaves[k] /= 1000 if leaves[k]>1000 else 1
        leaves[k] /= 1000
    total_count = sum([leaves[k] for k in leaves])

    # Find set of true HHHes based on leaf-node lambdas.
    #ratio = 0.05
    eta = total_count * ratio
    hhh_nodes = findHHH(leaves, eta)
    Smax = len(hhh_nodes)
    tHHH = [(node.l, node.k) for node in hhh_nodes]
    tHHH = sorted(tHHH, key = lambda x:x[0], reverse=True)
    logger.info("True HHHes: %s", ', '.join([str(k) for k in tHHH]))

    # Number of counters
    T = Smax*2+2

    # Run RWCB algo.
    sorted_leaf_tags = sorted(leaves.keys(), key = lambda x:x[1])
    lambda_lists = [leaves[k] for k in sorted_leaf_tags]

    name = 'Poisson'
    tmpFile = 'traffic_run_rwcb.txt'
    for i in range(iterations):
        # Generate one realization of traffic under Poisson distribution
        # leaf node lambdas are set as above.
        traffic_file = generate_traffic(lambda_lists, 1000, tmpFile)

        p_max = 1.0 - 1.0/float(2**(1.0/3))
        p0 = 0.9*p_max
        error, xi = 0.4, 1.0
        scale = 3.0*L*get_constant(p0)
        
        errorList = [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.499]
        for error in errorList:
            error_0 = error/float(2.0*Smax)

            # Run rwcb algo
            hhh_nodes, time_interval = run_one_instance(traffic_file, L, sorted_leaf_tags, name, p0, eta, error_0, scale, logging.WARNING, T, xi)
            mHHH = sorted(hhh_nodes.keys(), key = lambda x:x[0], reverse=True)
            o, p, r = error_function(mHHH, tHHH), precision(mHHH, tHHH), recall(mHHH, tHHH)
            logger.info("Iter {0}, Level {1}, Ratio {2}, Error {3}, Error0 {4}: Time interval {5}, Error_function {6}, Precision {7}, Recall {8}, Counter {9}".format(i, L, ratio, error, error_0, time_interval, o, p, r, T))

        if i % 50 == 0:
            print "Finished %d iterations..." % (i,)


def loop_outer():
    start_time = time.time()
    iters = 1000
    for L in range(9, 10):
        infile = "caida_data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(L)
        for ratio in [0.05]:
            loop_inner(L, infile, iters, ratio)
    end_time = time.time()
    print "Time elapsed: ", end_time - start_time

if __name__ == "__main__":
    loop_outer()

