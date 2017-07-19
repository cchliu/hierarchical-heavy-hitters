from rwcb_multi_statesman import rwcb_algo
from rwcb_multi_read import read_file

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
    
    # Instantiate one tree search object
    ts = rwcb_algo(threshold, p_zero, error, xi)
    ts.set_leaf_level(leaf_level)
    ts.init_start_node((0,1))
    ts.set_logging_level(logging.DEBUG)
    state = "state_one"
   
     
    while True:
        try:
            if state == "break":
                break
            line = read_file(ff)
            time_interval += 1
            ts.set_time_interval(time_interval)
            state = ts.statesman(state, line, leaf_level, HHH_nodes)
            print state
        except EOFError:
            LOG.error("Error: End of file error occurred.")
            break
    
    # Close file
    ff.close()

if __name__ == "__main__":
    main()

