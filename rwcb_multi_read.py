"""Feed aggregatd traffic count to the algorithm."""

def subtract_hhh(ns, HHH_nodes):
    """Modify the count of node by substracting the count 
    of its HHH decendants."""
    node = ns.node
    node_level, node_k = node
    hhh_descendants = []

    for hhh_node in HHH_nodes.keys():
        curr_level, curr_k = hhh_node
        while curr_level >= node_level:
            if node == (curr_level, curr_k):
                hhh_descendants.append(hhh_node)
            curr_level -= 1
            curr_k = (curr_k + 1) / 2

    # One HHH might be the descendant of another HHH
    # In this case, we only subtract the count of the HHH, which
    # is closer to the node.
    hhh_finalist = []
    hhh_descendants = sorted(hhh_descendants, key = lambda x: x[0], reverse=True)
    for idx, hhh_node in enumerate(hhh_descendants):
        curr_level, curr_k = hhh_node
        flag = False
        while curr_level >= node_level:
            if (curr_level, curr_k) in hhh_descendants[idx+1:]:
                flag = True
                break
            curr_level -= 1
            curr_k = (curr_k + 1) /2

        # This hhh node is not overshadowed by another hhh node, which
        # is closer to the node.
        if not flag:
            hhh_finalist.append(hhh_node)

    mod_x_mean = ns.x_mean
    for hhh_node in hhh_finalist:
        mod_x_mean -= HHH_nodes[hhh_node].x_mean
    return mod_x_mean

def update_hhh_count(line, leaf_level, HHH_nodes):
    """If the HHH_nodes set are not empty, for each identified HHH_node,
    keep counting the sample mean of it."""
    for node in HHH_nodes.keys():
        node_level, node_k = node
        node_val = 0
        for idx, val in enumerate(line):
            curr_level = leaf_level
            curr_k = idx + 1
            while(curr_level >= node_level):
                if node == (curr_level, curr_k):
                    node_val += val
                curr_level -= 1
                curr_k = (curr_k + 1) /2
        ns = HHH_nodes[node]
        ns.x_mean = (ns.x_mean * ns.s + node_val) / float(ns.s + 1.0)
        ns.s += 1.0

def update_hhh_set(ns, HHH_nodes):
    """Add newly detected HHH's into the HHH set."""
    node = ns.node
    if not node in HHH_nodes:
        HHH_nodes[node] = ns

def read_node(node, line, leaf_level):
    """Read traffic data of node at the current time_interval.
    
    If the HHH_nodes set are not empty, for each identified HHH_node,
    keep counting the sample mean of it.

    If the HHH_nodes set are not empty, the sample mean of all the parents 
    of an HHH_node is modified by subtracting the sample mean of this HHH_node.

        :param node: The node whose value to read.
        :param line: The packet count of all leaf nodes at the current time_interval.
        :param leaf_level: The leaf node level.
    """
    node_val = 0
    node_level, node_k = node
    for idx, val in enumerate(line):
        curr_level = leaf_level
        curr_k = idx + 1
        while(curr_level >= node_level):
            if node == (curr_level, curr_k):
                node_val += val
            curr_level -= 1
            curr_k = (curr_k + 1) / 2
    return node_val


def read_file(file_handler):
    ff = file_handler
    line = ff.readline().rstrip("\n")
    if not line:
        raise EOFError
    line = [int(k) for k in line.split(',')]
    return line
