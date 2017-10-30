"""
    Find set of HHH's offline offline.
"""
import time
import math

def load_lambdas(infile, scale=False):
    """
    :param infile: Read one instance of caida trace. Use the value as the leaf lambdas.
        
    :returns: leaf lambdas, a list of [(l,k),lambda].
    """
    leaf_lambdas = {}
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n').split(',')
            l, k, count = [int(i) for i in line]
            leaf_lambdas[(l,k)] = count

    if scale:
        # Scale leaf lambdas, < 100
        max_lambda = max([leaf_lambdas[k] for k in leaf_lambdas])
        x1 = int(math.log(max_lambda, 10))
        if x1 > 2:
            x2 = x1 - 2
            for k in leaf_lambdas:
                leaf_lambdas[k] = int(leaf_lambdas[k] / float(10**x2))
    return leaf_lambdas

class Node(object):
    def __init__(self, l, k, val):
        self.l, self.k = l, k
        self.val = val
        # Count contribution to the parent code
        self.net_val = 0

def findHHH(dvalues, threshold):
    """
    :param dvalues: A dictionary with key = (l,k) and val = node count.
    :param threshold: A node is an HHH if its count > threshold.

    :return: A list of HHH nodes.

    """
    curr_level = []
    for (l,k) in dvalues:
        val = dvalues[(l,k)]
        node = Node(l, k, val)
        curr_level.append(node)

    hhh_nodes = []
    while len(curr_level) and curr_level[0].l>=0:
        #print "Processing level ", curr_level[0].l
        for node in curr_level:
            if node.val > threshold:
                # Declare node as an HHH
                node.net_val = 0
                hhh_nodes.append(node)
            else:
                node.net_val = node.val

        # Aggreate node count to the parent level
        parent_level = {}
        for node in curr_level:
            l, k = node.l, node.k
            pl, pk = l-1, k/2
            if not (pl,pk) in parent_level:
                parent_level[(pl,pk)] = Node(pl, pk, 0)
            parent_level[(pl,pk)].val += node.net_val

        curr_level = [parent_level[k] for k in parent_level]
    
    return hhh_nodes

def main():
    start_time = time.time()
    
    dvalues = {}
    infile = "caida_data/equinix-chicago.dirA.20160406-140200.UTC.anon.agg.l8.csv"
    dvalues = load_lambdas(infile)

    total_pkts = sum([dvalues[k] for k in dvalues])
    print "Total pkts: ", total_pkts
   
    for ratio in [0.1, 0.09, 0.08]:
        threshold = total_pkts * ratio
        print "Threshold: ", threshold
    
        hhh_nodes = findHHH(dvalues, threshold)
        for hhh_node in hhh_nodes:
            print (hhh_node.l, hhh_node.k), hhh_node.val

    end_time = time.time()
    print "Total time elapsed: ", end_time-start_time

if __name__ == "__main__":
    main()
