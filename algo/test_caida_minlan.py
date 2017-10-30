"""
### Read values of current time interval.
### Update the rules online.

"""
import logging

from minlan_algo import MinlanAlgo

from tree_operations import construct
from module.generator import generate_traffic
from module.offline_caida import load_lambdas, findHHH
from module.metric import precision, recall, error_function

def run_one_instance(tHHH, infile, L, sorted_leaf_tags, eta, Smax, logging_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    monitor = MinlanAlgo(L, eta, Smax, logging_level)
    time_interval, ret = 0, []
    with open(infile, 'rb') as ff:
        for line in ff:
            time_interval += 1
            values = [int(k) for k in line.rstrip().split(',')]
            dvalues = construct(values, sorted_leaf_tags)
            hhh_nodes = monitor.run(dvalues)

            mHHH = sorted([(node.l, node.k) for node in hhh_nodes], key = lambda x:x[0], reverse=True)
            o, p, r = error_function(mHHH, tHHH), precision(mHHH, tHHH), recall(mHHH, tHHH)
            ret.append([o, p, r])
            logger.debug("Level %d, At time interval %d, Error_function %d, Precision %f, Recall %f", L, time_interval, o, p, r)
            logger.debug("True HHHes: %s", ', '.join([str(k) for k in tHHH]))
            logger.debug("Measured HHHes: %s", ', '.join([str(k) for k in mHHH]))
    return ret            

def loop_inner(L, infile, iters):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # leaves: A dictionary with key = (l,k), value = lambda
    leaves = load_lambdas(infile)
    for k in leaves:
        #leaves[k] /= 1000 if leaves[k]>1000 else 1
        leaves[k] /= 1000
    total_count = sum([leaves[k] for k in leaves])

    # Find set of true HHHes based on leaf-node lambdas.
    ratio = 0.05
    eta = total_count * ratio
    hhh_nodes = findHHH(leaves, eta)
    Smax = len(hhh_nodes)
    tHHH = [(node.l, node.k) for node in hhh_nodes]
    tHHH = sorted(tHHH, key = lambda x:x[0], reverse=True)
    logger.info("True HHHes: %s", ', '.join([str(k) for k in tHHH]))

    sorted_leaf_tags = sorted(leaves.keys(), key = lambda x:x[1])
    lambda_lists = [leaves[k] for k in sorted_leaf_tags]

    tmpFile = "traffic_tmp_minlan.txt" 
    result = []
    for i in range(iters):
        # Generate one realization of traffic under Poisson distribution
        # leaf node lambdas are set as above.
        traffic_file = generate_traffic(lambda_lists, 1000, tmpFile)
        one_result = run_one_instance(tHHH, traffic_file, L, sorted_leaf_tags, eta, Smax, logging.DEBUG)
        if not result:
            result = one_result
        else:
            result = [[pair[k]+one_result[idx][k] for k in range(3)] for idx, pair in enumerate(result)]
    
    result = [[pair[k]/float(iters) for k in range(3)] for pair in result]
    for idx, pair in enumerate(result):
        o, p, r = pair
        print "Level %d, Ratio %f, Iterations %d, At time interval %d, Error_function %f, Precision %f, Recall %f" % (L, ratio, iters, idx+1, o, p, r)
 

def loop_outer():
    iters = 1
    for L in range(9, 10):
        infile = "caida_data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l{0}.csv".format(L)
        loop_inner(L, infile, iters)

if __name__ == "__main__":
    loop_outer()

