"""
    Find set of HHH's offline.
    Different from version #1 where the complete binary tree is constructed, 
    in this version, we only create nodes that are parent of exisiting leaf node.
"""
class Node(object):
    def __init__(self, val, tag):
        self.par = None
        self.left = None
        self.right = None
        self.tag = tag
        self.val = val
        self.HHH_val = 0

def createTree(leaf_nodes, threshold):
    """
        :param leaf_nodes: a list of lists [(l,k), val] for leaf_nodes
    """
    # Keeping track of nodes that have been created.
    # key: (l,k), val: an :class:`.Node` object.
    has_nodes = {}
    for (l,k), count in leaf_nodes:
        if not (l,k) in has_nodes:
            has_nodes[(l,k)] = Node(count, (l,k))
            has_nodes[(l,k)].HHH_val = count
        
        curr_l, curr_k = l, k
        curr_tag = (curr_l, curr_k)
        while(curr_l >= 1):
            up_l = curr_l - 1
            up_k = (curr_k + 1) / 2
            up_tag = (up_l, up_k)
            if not up_tag in has_nodes:
                has_nodes[up_tag] = Node(count, up_tag)
            else:
                has_nodes[up_tag].val += count
            has_nodes[curr_tag].par = has_nodes[up_tag]
            
            if curr_k % 2 == 0:
                if has_nodes[up_tag].right == None:
                    has_nodes[up_tag].right = has_nodes[curr_tag]
            else:
                if has_nodes[up_tag].left == None:
                    has_nodes[up_tag].left = has_nodes[curr_tag]
            curr_l, curr_k  = up_l, up_k
            curr_tag = (curr_l, curr_k)
  
    #print "In total, we create {0} Nodes.".format(len(has_nodes))

    # Calculate HHH_val
    curr_nodes = [k[0] for k in leaf_nodes]
    
    while curr_nodes:
        uplevel_nodes = []
        for node_tag in curr_nodes:
            curr_node = has_nodes[node_tag]
            par_node = curr_node.par
            if par_node != None:
                if curr_node.HHH_val  < threshold:
                    par_node.HHH_val += curr_node.HHH_val
                if par_node.tag not in uplevel_nodes:
                    uplevel_nodes.append(par_node.tag)
        curr_nodes = uplevel_nodes

    root = has_nodes[(0,1)]
    return (root, has_nodes)

def findHHH(root, threshold):
    curr_nodes = [root]
    HHH_nodes = []
    while(curr_nodes):
        next_nodes = []
        for node in curr_nodes:
            if node.left:
                next_nodes.append(node.left)
            if node.right:
                next_nodes.append(node.right)
            if node.HHH_val >= threshold:
                HHH_nodes.append(node.tag)
        curr_nodes = next_nodes
    return HHH_nodes

def sortTree(tree):
    """Sort tree node based on HHH_val."""
    sorted_nodes = sorted(tree.keys(), key = lambda x:tree[x].HHH_val, reverse=True)
    print "Top 20 HHH_val:"
    for node in sorted_nodes[:30]:
        print node, tree[node].HHH_val     

def main(infile):
    leaf_nodes = []
    leaf_level = 16

    #infile = "equinix-chicago.dirA.20160406-140200.UTC.anon.agg.csv"
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n').split(',')
            prefix, val = line[0], int(line[1])
            b1, b2 = [int(k) for k in prefix.split('.')]
            index = b1 * 256 + b2 + 1
            tag = (leaf_level, index)
            leaf_nodes.append([tag, val])

    total_pkts = sum([k[1] for k in leaf_nodes])
    print total_pkts

    threshold = total_pkts * 0.1
    print threshold
    root,tree = createTree(leaf_nodes, threshold)
    print root.val
    HHH_nodes = findHHH(root, threshold) 
    print HHH_nodes
    print len(HHH_nodes)
    
    sortTree(tree)


if __name__ == "__main__":
    import os, glob
    
    infiles = glob.glob("*.agg.csv")
    for infile in infiles:
        main(infile)
