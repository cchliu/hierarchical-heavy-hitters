"""
### Read a value at each time interval
### Change the state of the pointer.

"""
import logging

from module.helper import get_constant
from tree_operations import construct
from single_target_poisson import Pointer_Poisson

def main():
    infile = 'traffic_8nodes_poisson.txt'
    L = 3
    # Parameters
    p_max = 1.0 - 1.0/float(2**(1.0/3))
    p0 = 0.9*p_max
    error, eta = 0.4, 25
    xi = 1.0

    # Sorted leaf tags
    sorted_leaf_tags = [(L, idx) for idx in range(8)]

    # Instantiate a pointer
    #scale = 3.0*L*get_constant(p0)
    scale = 1.0
    l, k = 0, 0
    pntr = Pointer_Poisson(l, k, L, p0, eta, error, scale, logging.DEBUG, xi)
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
