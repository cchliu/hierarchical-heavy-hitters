import math
import collections

from tree_operations import construct, read_hhh_nodes
from multi_target_poisson import Pointer_Poisson

def get_pntr(name, *args, **kwargs):
    if name == "Poisson":
        return Pointer_Poisson(*args, **kwargs)

def split_tree(L, T):
    """
    :param L: The depth of the tree.
    :param T: The number of remaining counters.

    :return: A list of starting nodes for subtrees.
    """
    ret = []
    if 2**L < T:
        T = 2**L
    l0 = int(math.log(T, 2))
    # Number of nodes at level l0
    m0 = 2**l0 - (T-2**l0)
    for i in range(m0):
        ret.append((l0, i))
    for i in range(m0, 2**l0):
        ret.append((l0+1, i*2))
        ret.append((l0+1, i*2+1))
    return ret


def run_one_instance(infile, L, leaf_tags, name, p0, eta, error, scale, logging_level, T, *args, **kwargs):
    #infile = 'traffic_tmp.txt'
    # Maintain a list of Pointer objects
    pntrs = collections.deque()

    # Instantiate initial pointers
    starting_nodes = split_tree(L, T)
    for idx, (l, k) in enumerate(starting_nodes):
        pntr = get_pntr(name, l, k, L, p0, eta, error, scale, logging_level, idx, *args, **kwargs)
        #pntr = Pointer_Poisson(l, k, L, p0, eta, error_0, xi, logging.WARNING, idx)
        pntrs.append(pntr)
    time_interval = 0

    # Keep monitoring detected HHH nodes
    # key: (l,k), val: newNode object
    HHH_nodes = {}

    isActive = True
    with open(infile, 'rb') as ff:
        for line in ff:
            time_interval += 1
            values = [int(k) for k in line.split(',')]
            dvalues = construct(values, leaf_tags)

            # Keep monitoring detected HHH nodes
            read_hhh_nodes(dvalues, HHH_nodes)

            # Moving the pointers
            lenth = len(pntrs)
            for i in range(lenth):
                pntr = pntrs.popleft()
                hhh_node = pntr.run(dvalues, HHH_nodes)

                # If found a new HHH node, add it to the HHH_nodes set.
                if hhh_node and not (hhh_node.l, hhh_node.k) in HHH_nodes:
                    HHH_nodes[(hhh_node.l, hhh_node.k)] = hhh_node
                    # Assign this pointer to keep monitoring this HHH node
                else:
                    pntrs.append(pntr)

                if not pntr.isActive():
                    isActive = False
                    break
            if not isActive:
                break
    return [HHH_nodes, time_interval]

