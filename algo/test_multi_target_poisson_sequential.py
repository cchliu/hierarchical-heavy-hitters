import logging

from module.helper import get_constant
from tree_operations import construct, read_hhh_nodes 
from multi_target_poisson import Pointer_Poisson


def main():
    infile = 'traffic_8nodes_poisson_multi.txt'
    L = 3
    # Parameters
    p_max = 1.0 - 1.0/float(2**(1.0/3))
    p0 = 0.9*p_max
    error, eta = 0.4, 25
    xi = 1.0
    Smax = 2
    error_0 = error/float(2.0*Smax)

    # Instantiate a pointer
    #scale = 3.0*L*get_constant(p0)
    scale = 1.0
    l, k = 0, 0
    pntr = Pointer_Poisson(l, k, L, p0, eta, error_0, scale, logging.DEBUG, 0, xi)
    time_interval = 0

    # Sorted leaf tags
    sorted_leaf_tags = [(L, idx) for idx in range(8)]

    # Keep monitoring detected HHH nodes
    # key: (l,k), val: newNode object
    HHH_nodes = {}

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

if __name__ == "__main__":
    main()

