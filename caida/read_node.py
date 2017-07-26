"""
    :param leaf_nodes: A list of leaf_nodes with (l,k) and count
"""
def read_node(node, leaf_nodes, leaf_level):
    """Read traffic data of node at the current time_interval.

    :param node: The node to monitor.
    :param leaf_nodes: A list of leaf_nodes with (l,k) and count.
    :param leaf_level: The leaf node level. 
    """
    node_val = 0
    node_level, node_k = node
    for (l,k), count in leaf_nodes:
        curr_level, curr_k = l, k
        while(curr_level >= node_level):
            if node == (curr_level, curr_k):
                node_val += count
            curr_level -= 1
            curr_k = (curr_k + 1) / 2
    return node_val 
