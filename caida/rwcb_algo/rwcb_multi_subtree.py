import sys
import logging
import math
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rwcb_multi_hhh import update_hhh_count
from read_file import read_file
from parallel_rwcb import parallel_rwcb_algo
from offline_caida import createTree, findHHH
#---------------------------------------------#
# logging
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#---------------------------------------------#

def main():
    infile = "traffic_twoHHH.txt"
    infile = "traffic.txt"
    leaf_level = 3
    p_init = 1 - 1.0 / (2**(1.0/3.0))
    p_zero = p_init * 0.9
    error = p_init * 0.5
    xi = 1.0
    threshold = 25

    #----------------------------------------#
    # Find true universal set of HHHes.
    #----------------------------------------#    
    leaf_lambdas = [[(3,1),20], [(3,2),10], [(3,3),1], [(3,4),1], [(3,5),1], [(3,6),1], [(3,7),1], [(3,8),1]]
    root,tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)
    print "Truee HHHes: ", tHHH_nodes

    S = 1
    pts = parallel_rwcb_algo(leaf_level, threshold, p_zero, error, xi, S, logging.DEBUG)
    ff = open(infile, 'rb')
    while True:
        try:
            line = read_file(ff, leaf_level)
            flag = pts.run(line) 
            if flag:
                break
        except EOFError:
            LOG.error("Error: End of file error occurred.")
            break

    tHHH_nodes = [(2,1)]
    pts.report(tHHH_nodes) 
    # Close file
    ff.close()
         

if __name__ == "__main__":
    main()
