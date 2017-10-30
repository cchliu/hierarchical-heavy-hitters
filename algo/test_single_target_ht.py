"""
### Read a value at each time interval
### Change the state of the pointer.

"""
import logging
import math

from module.helper import get_constant
from tree_operations import construct
from single_target_ht import Pointer_HT

def main():
    infile = 'traffic_8nodes_ht.txt'
    L = 3
    # Parameters
    p_max = 1.0 - 1.0/float(2**(1.0/3))
    p0 = 0.9*p_max
    error, eta = 0.4, 25
    b, u = 2, 810
    # Scale for test functions
    Fval = 4*u**(1/float(b))*(math.log(2.0*1.0**3/float(p0))/float(1.0))**((b-1)/float(b))
    cF = eta/float(Fval)
    # Sorted leaf tags
    sorted_leaf_tags = [(L, idx) for idx in range(8)]

    # Instantiate a pointer
    l, k = 0, 0
    #scale = 3.0*L*get_constant(p0)
    scale = 1.0

    pntr = Pointer_HT(l, k, L, p0, eta, error, scale, logging.DEBUG, b, u, cF)
    time_interval = 0

    with open(infile, 'rb') as ff:
        for line in ff:
            time_interval += 1
            values = [int(k) for k in line.split(',')]
            dvalues = construct(values, sorted_leaf_tags)
            pntr.run(dvalues)
            if not pntr.isActive():
                break
    print "Time interval: %d" % time_interval

if __name__ == "__main__":
    main()
