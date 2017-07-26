"""
    Test yu's algorithm.
    - Will precision and recall converge?

    Read one instance of caida trace and use the values as leaf lambdas.
    Scale lambdas.
    Generate synthetic traces following Poisson distribution.

    - Starting nodes to monitor:
        - S: The number of HHH nodes
        - 2**(l_0) <= S < 2**(l_0+1)
        - Nodes to monitor at level l_0: 
            - 2**(l_0) - (S-2**(l_0)) = 2**(l_0+1)-S
        - Nodes to monitor at level l_0 + 1: 
            - 2*(S - 2**(l_0))= 2S - 2**(l_0+1)    

    - Run offline algorithm to report true HHHes within this time interval.
    - Run Yu's algorithm, report HHH and calculate precision and recall. 
"""

import math
from generator import generator
from tree_operation import parent, left_child, right_child, sibling
from offline_caida import createTree, findHHH
from yu_algo import yu_algo
from metric import precision, recall

def main():
    # Read one instance of caida trace. Use the value as the leaf lambdas.
    leaf_lambdas = []
    leaf_level = 16

    infile = "equinix-chicago.dirA.20160406-140200.UTC.anon.agg.csv"
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n').split(',')
            prefix, val = line[0], int(line[1])
            b1, b2 = [int(k) for k in prefix.split('.')]
            index = b1 * 256 + b2 + 1
            tag = (leaf_level, index)
            val = int(float(val) / 10000)
            leaf_lambdas.append([tag, val])
    total = sum([k[1] for k in leaf_lambdas])
    threshold = total * 0.1
    
    #----------------------------------------#
    # Find true universal set of HHHes.
    #----------------------------------------#    
    root,tree = createTree(leaf_lambdas, threshold)
    tHHH_nodes = findHHH(root, threshold)

    # Find start nodes to monitor
    S = 10
    num_of_TCAM = 2*S + 2

    l0 = int(math.log(S, 2))
    l0_num = 2**(l0+1) - S
    l1_num = 2*S - 2**(l0+1)

    curr_monitors = []
    for i in range(l0_num):
        node = (l0, i+1)
        curr_monitors.append(node)

    for i in range(l0_num, 2**l0):
        node = (l0+1, (i+1)*2)
        curr_monitors.append(node)
        node = (l0+1, (i+1)*2-1)
        curr_monitors.append(node)
    
    # Find start nodes to measure
    curr_nodes = []
    for node in curr_monitors:
        node_l, node_k = node
        if node_l == leaf_level:
            # Leaf node
            curr_nodes.append(node)
        else:
            # Non-leaf node
            left_child_node, right_child_node = left_child(node, leaf_level), right_child(node, leaf_level)
            curr_nodes.append(left_child_node)
            curr_nodes.append(right_child_node)

    # Always monitor the root
    #print "Initial measuring nodes: ", curr_nodes

    # Run yu's algorithm to calculate precision and recall. 
    iterations = 1000
    for i in range(iterations):
        traffic = generator(leaf_lambdas)
        #------------------------------------------#
        # Run offline algorithm to report true HHHes
        # This case: we have temporary set of HHHes in each time interval.
        #------------------------------------------#
        #root,tree = createTree(traffic, threshold)
        #tHHH_nodes = findHHH(root, threshold)
        #print "True hhhes: ", tHHH_nodes
        
        # Run yu's algorithm 
        rHHH_nodes, next_nodes = yu_algo(curr_nodes, traffic, leaf_level, threshold, num_of_TCAM)
        #print "Reported hhhes: ", rHHH_nodes
        
        # Calculate precision and recall
        p = precision(rHHH_nodes, tHHH_nodes)
        r = recall(rHHH_nodes, tHHH_nodes)
        print "precision: {0}, recall: {1}".format(p, r)
        curr_nodes = next_nodes


if __name__ == "__main__":
    main()
