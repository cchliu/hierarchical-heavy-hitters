from rwcb_multi_statesman import rwcb_algo
from rwcb_multi_read import read_file, update_hhh_count

import sys
import logging
import math
#---------------------------------------------#
# logging
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# :param time_interval: the index of current time interval
global time_interval

# :param threshold: HHH threshold
# :param epsno: parameter in equation (31) or (32)
# :param p_zero: initialize p_zero
global threshold, xi, p_zero, error
p_init = 1 - 1.0 / (2**(1.0/3.0))
p_zero = p_init * 0.9
error = p_init * 0.5
xi = 6.0
threshold = 25


def main():
    # Read from file
    infile = "traffic_twoHHH.txt"
    ff = open(infile, 'rb')

    # :param time_interval: The index of current time interval.
    time_interval = 0

    # Parameters about the tree
    # :param leaf_level: The depth of the tree.
    leaf_level = 3

    # :param HHH_nodes: a list to store detected HHH's
    # key: (l, k), value: :class:`node_status' 
    HHH_nodes = {}

    #----------------------------------------------------#
    """Divide into subtrees."""
    # :param N: The number of counters
    # :param S: The number of HHH's
    N, S = 3, 2
    M = N -S + 1
    # 2^l0 <= M < 2^(l0+1)
    l0 = int(math.log(M, 2))
    l1 = l0 + 1
    # :param n0: Number of subtrees with roots on level l0
    # :param n1: Number of subtrees with roots on level l1
    n1 = 2*(M - 2**l0)
    n0 = 2**(l1) - M
    
    # A list of subtree search objects
    # And its corresponding states
    subts, states = [], []
    for i in range(M):
        if i < n0:
            root_node = (l0, i+1)
        else:
            root_node = (l1, n0+i+1) 
    
        # Instantiate subtree search object
        ts = rwcb_algo(threshold, p_zero, error, xi)
        ts.set_leaf_level(leaf_level)
        ts.init_start_node(root_node)
        ts.set_logging_level(logging.DEBUG)    
        subts.append(ts)
        states.append("state_one")
    #-------------------------------------------------------#       
    num_of_subts = len(subts)
    next_subts, next_states = [], []
    while num_of_subts:
        # Not all subtrees finish searching.
        try:
            line = read_file(ff)
            time_interval += 1
            update_hhh_count(line, leaf_level, HHH_nodes)
            for idx, ts in enumerate(subts):
                ts.set_time_interval(time_interval)
                state = states[idx]
                state = ts.statesman(state, line, leaf_level, HHH_nodes)
                if state == "break":
                    num_of_subts -= 1
                else:
                    next_subts.append(ts)
                    next_states.append(state)
                    
            subts = next_subts
            states = next_states
            next_subts, next_states = [], []
        except EOFError:
            LOG.error("Error: End of file error occurred.")
    # Close file
    ff.close()

if __name__ == "__main__":
    main()

