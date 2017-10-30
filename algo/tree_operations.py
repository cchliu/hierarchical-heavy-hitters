"""
Tree Operations
"""
def construct(values, leaf_tags):
    # Add leaf_index (leaf_l, leaf_k) to values.
    d = {}
    for idx in range(len(values)):
        d[leaf_tags[idx]] = values[idx]
    return d

def read(l, k, leaf_nodes):
    """
    :param leaf_nodes: A dict with leaf node index (leaf_l, leaf_k) and value
    :param l, k: level, index of monitored node
    """
    ret = 0
    for leaf_node in leaf_nodes:
        leaf_l, leaf_k = leaf_node
        value = leaf_nodes[leaf_node]
        while leaf_l>=0:
            if leaf_l == l and leaf_k == k:
                ret += value
            leaf_l, leaf_k = leaf_l-1, leaf_k/2
    return ret

def read_hhh_nodes(dvalues, HHH_nodes):
    # Update x_mean and s for declared HHH nodes.
    for hhh_tag in HHH_nodes:
        node = HHH_nodes[hhh_tag]
        val = read(node.l, node.k, dvalues)
        x_mean = (node.x_mean * node.s + val) / float(node.s + 1.0)
        node.x_mean, node.s = x_mean, node.s+1.0
        node.x_mean_net = node.x_mean

    # Calculate net average count of HHH nodes excluding its HHH descendants.
    sorted_nodes = sorted(HHH_nodes.keys(), key = lambda x:x[0], reverse=True)
    for l,k in sorted_nodes:
        val = HHH_nodes[(l,k)].x_mean_net
        tmp_l, tmp_k = l-1, k/2
        while tmp_l >=0:
            if (tmp_l, tmp_k) in HHH_nodes:
                HHH_nodes[(tmp_l, tmp_k)].x_mean_net -= val
            tmp_l, tmp_k = tmp_l-1, tmp_k/2

    # Reset to 0 if x_mean_net < 0:

def read_multi(node, dvalues, HHH_nodes):
    # Read aggregated value of node
    # Update x_mean and s
    val = read(node.l, node.k, dvalues)
    ret = val

    #func(node, val, *args, **kwargs)
    x_mean = (node.x_mean * node.s + val) / float(node.s + 1.0)
    node.x_mean, node.s = x_mean, node.s+1.0
    node.x_mean_net = node.x_mean

    # Subtract contribution from HHH descendants.
    for hhh_tag in HHH_nodes:
        val = HHH_nodes[hhh_tag].x_mean_net 
        tmp_l, tmp_k = hhh_tag
        while tmp_l >=0:
            if (tmp_l, tmp_k) == (node.l, node.k):
                node.x_mean_net -= val
                break
            tmp_l, tmp_k = tmp_l-1, tmp_k/2
    return ret

#***************************************#
def get_parent(l, k):
    if l == 0:
        # Root node
        return (0, 0)
    else:
        parent_l = l-1
        parent_k = k/2
        return (parent_l, parent_k)

def get_left_child(l, k, leaf_l):
    if l == leaf_l:
        return None
    left_child_l, left_child_k = l+1, k*2
    return (left_child_l, left_child_k)

def get_right_child(l, k, leaf_l):
    if l == leaf_l:
        return None
    right_child_l, right_child_k = l+1, k*2+1
    return (right_child_l, right_child_k)

def get_sibling(l, k):
    if l==0:
        return None
    else:
        if k % 2 == 0:
            return (l, k+1)
        if k % 2 == 1:
            return (l, k-1)
