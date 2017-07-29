"""
    Algo:
    - Always monitor the root. Two counters monitor the children of root.
    - Starting nodes to monitor:
        - S: The number of HHH nodes
        - 2**(l_0) <= S < 2**(l_0+1)
        - Nodes to monitor at level l_0: 
            - 2**(l_0) - (S-2**(l_0)) = 2**(l_0+1)-S
        - Nodes to monitor at level l_0 + 1: 
            - 2*(S - 2**(l_0))= 2S - 2**(l_0+1)
        - Of course, if a node is monitored, we install rules to measure
        its two children.
"""
import os
import sys
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from offline_caida import createTree, findHHH
from read_node import read_node
from tree_operation import parent, left_child, right_child, sibling

def yu_algo_main(curr_nodes, leaf_nodes, leaf_level, threshold, num_of_TCAM):
    """
        :param curr_nodes: Current measurement nodes. We meansure the children of
        monitoring nodes.
        :param leaf_nodes: Leaf node count input in the current time interval.
        :param leaf_level: Leaf node level.
        :param threshold: HHH threshold.
        :param num_of_TCAM: Number of TCAM entries available to use.

        :returns: reported HHHes & measurement nodes in the next time interval.

        Read counts for all measurement nodes.
        Process the counts as TCAM entries, the same packet won't count twice
        in more than one TCAM rule.
        createTree based on post-processed measurements.
        findHHH in the tree to report.
        find measurement nodes from HHHes. children of HHHes.
        always monitor the root node.
        sort exisitng HHHes in increasing order. 
        Measure siblings of lowest spare number of HHHes.
    """
    # Read the aggregated count for all measurement nodes.
    # key: node_tag, val: count
    curr_vals = {}
    for curr_node in curr_nodes:
        val = read_node(curr_node, leaf_nodes, leaf_level)
        curr_vals[curr_node] = val

    # Process the counts as TCAM entries, the same packet won't count twice
    sorted_nodes = sorted(curr_nodes, key = lambda x:x[0])
    for node in sorted_nodes:
        curr_l, curr_k = node
        curr_l -= 1
        curr_k = (curr_k + 1 )/2
        par_node = (curr_l, curr_k)
        while(curr_l >= 0):
            if par_node in curr_vals:
                curr_vals[par_node] -= curr_vals[node]
            curr_l -= 1
            curr_k = (curr_k + 1) / 2
    
    # Create tree based on post-processed measurements.
    input_nodes = [[node_tag, curr_vals[node_tag]] for node_tag in curr_vals]
    #print "curr measurement nodes: ", curr_nodes
    root, tree = createTree(input_nodes, threshold)

    # Find HHHes in the tree to report.
    HHH_nodes = findHHH(root, threshold)

    # Find measurement nodes from reported HHHes. Children of HHHes.
    next_nodes = []
    for hhh_node in HHH_nodes:
        hhh_node_l, hhh_node_k = hhh_node
        if hhh_node_l == leaf_level:
            # Leaf node
            next_nodes.append(hhh_node)
        else:
            # Non-leaf node
            left_child_node, right_child_node = left_child(hhh_node, leaf_level), right_child(hhh_node, leaf_level)
            next_nodes.append(left_child_node)
            next_nodes.append(right_child_node)
    
    # Always monitor the root
    if (1,1) not in next_nodes:
        next_nodes.append((1,1))
    if (1,2) not in next_nodes:
        next_nodes.append((1,2))

    # If there are spare entries
    if len(next_nodes) < num_of_TCAM:
        # Sort existing HHHes in increasing order
        sorted_hhh_nodes = sorted(HHH_nodes, key = lambda x:tree[x].HHH_val) 
        
        # Measure siblings of HHHes of lowest counts
        used_TCAM = len(next_nodes)
        for hhh_node in sorted_hhh_nodes:
            sibling_node = sibling(hhh_node, 0)
            if sibling_node and not sibling_node in next_nodes:
                next_nodes.append(sibling_node)
                used_TCAM += 1
                if used_TCAM >= num_of_TCAM:
                    break    
     
    used_TCAM = len(next_nodes) 
    if used_TCAM < num_of_TCAM:
        print "Warning: not using all available TCAMs, using {0} TCAMs, available {1} TCAMs".format(used_TCAM, num_of_TCAM)
    return (HHH_nodes, next_nodes)
     

if __name__ == "__main__":
    main()
