"""
    Operations in tree structure.
    - parent of a node 
    - left child of a node
    - right child of a node
    - sibling of a node
"""
def parent(node_tag, root_level):
    node_l, node_k = node_tag
    if node_l == root_level:
        return node_tag
    else:
        node_l = node_l - 1
        node_k = (node_k + 1) / 2
        return (node_l, node_k)

def left_child(node_tag, leaf_level):
    node_l, node_k = node_tag
    if node_l == leaf_level:
        return None
    else:
        node_l += 1
        node_k = node_k * 2 -1
        return (node_l, node_k)

def right_child(node_tag, leaf_level):
    node_l, node_k = node_tag
    if node_l == leaf_level:
        return None
    else:
        node_l += 1
        node_k = node_k * 2
        return (node_l, node_k)

def sibling(node_tag, root_level):
    node_l, node_k = node_tag
    if node_l == root_level:
        return None
    else:
        if node_k % 2 == 0:
            # Sibling is left child
            return (node_l, node_k-1)
        else:
            # Sibling is right child
            return (node_l, node_k+1)
