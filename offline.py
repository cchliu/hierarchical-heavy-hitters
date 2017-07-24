# Find set of HHH's offline

class Node(object):
    def __init__(self, val):
        self.par = None
        self.left = None
        self.right = None
        self.tag = (0, 0) 
        self.val = val
        self.HHH_val = 0

def createTree(levels):
    root = Node(0)
    root.tag = (0, 1)
    curr_level = [root]
    for i in range(1, levels):
        next_level = []
        curr_counter = 0
        for node in curr_level:
            node.left = Node(0)
            node.left.par = node
            curr_counter += 1
            node.left.tag = (i, curr_counter)
            next_level.append(node.left)            

            node.right = Node(0)
            node.right.par = node
            curr_counter += 1
            node.right.tag = (i, curr_counter)
            next_level.append(node.right)

        curr_level = next_level
    # return a list of leaf nodes
    return (root, curr_level)

def fillTree(leaf_nodes, vals, threshold):
    for i, leaf_node in enumerate(leaf_nodes):
        leaf_node.val = vals[i]
        leaf_node.HHH_val = vals[i]

    for leaf_node in leaf_nodes:
        curr_node = leaf_node
        while(curr_node.par != None):
            curr_node.par.val += leaf_node.val
            curr_node = curr_node.par
 
    curr_nodes = leaf_nodes
    level_up_nodes = []
    level_up_tags = set()
    while curr_nodes:
        level_up_nodes = []
        level_up_tags = set()
        for node in curr_nodes:
            if node.par != None:
                if node.HHH_val >= threshold:
                    node.par.HHH_val += 0
                else:
                    node.par.HHH_val += node.HHH_val
                if not node.par.tag in level_up_tags:
                    level_up_nodes.append(node.par)
                    level_up_tags.add(node.par.tag)
        curr_nodes = level_up_nodes            

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
                #print "t = {0}, node {1} is an HHH".format(counter, node.tag)
        curr_nodes = next_nodes
    return HHH_nodes

def clearTree(root):
    curr_nodes = [root]
    while curr_nodes:
        next_nodes = []
        for node in curr_nodes:
            node.val, node.HHH_val = 0, 0
            if node.left:
                next_nodes.append(node.left)
            if node.right:
                next_nodes.append(node.right)
        curr_nodes = next_nodes
       
def printTree(root):
    curr_nodes = [root]
    while curr_nodes:
        next_nodes = []
        for node in curr_nodes:
            print "node {0} val:{1}, HHH_val:{2}".format(node.tag, node.val, node.HHH_val)
            if node.left:
                next_nodes.append(node.left)
            if node.right:
                next_nodes.append(node.right)
        curr_nodes = next_nodes   

def main():
    # Create a binary tree
    levels = 4
    root, leaf_nodes = createTree(levels)
    threshold = 7 * 2**(levels)
    
    # Clear tree
    clearTree(root)
    printTree(root)
     
    # Read traffic data
    infile = "traffic.txt"
    infile = "traffic_twoHHH.txt"
    infile = "traffic_tmp.txt"
    global counter
    counter = 0 
    with open(infile, 'rb') as ff:
        for line in ff:
            counter += 1
            line = line.rstrip('\n').split(',')
            line = [int(k) for k in line]
            if counter < 50:
                fillTree(leaf_nodes, line, threshold)
                HHH_nodes = findHHH(root, threshold)
                output = ["node {0}".format(node_tag) for node_tag in HHH_nodes]
                outstr = ','.join(output)
                print "t={0}, ".format(counter) + outstr + " are HHH's"
                clearTree(root)
    

if __name__ == "__main__":
    main()
     
         
