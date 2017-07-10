# Find set of HHH's offline

class Node(object):
    def __init__(self, val):
        self.par = None
        self.left = None
        self.right = None
        self.val = val
        self.HHH_val = 0

def createTree(levels):
    root = Node(0)
    curr_level = [root]
    for i in range(1, levels):
        next_level = []
        for node in curr_level:
            node.left = Node(0)
            node.left.par = node
            node.right = Node(0)
            node.right.par = node
            next_level.append(node.left, node.right)
        curr_level = next_level
    # return a list of leaf nodes
    return curr_level

def fillTree(leaf_nodes, vals, threshold):
    for i, leaf_node in enumerate(leaf_nodes):
        leaf_node.val = vals[i]
        leaf_node.HHH_val = vals[i]

    for leaf_node in leaf_nodes:
        curr_node = leaf_node
        while(curr_node.par != None):
            curr_node.par.val += curr_node.val
            curr_node = curr_node.par
            if curr_node.HHH_val >= threshold:
                curr_node.par.HHH_val += 0
            else:
                curr_node.par.HHH_val += curr_node.par.HHH_val

def findHHH(root):
    curr_nodes = [root]
    while(curr_nodes):
        next_nodes = []
        for node in curr_nodes:
            if node.HHH_val >= threshold:
                print "node
    

