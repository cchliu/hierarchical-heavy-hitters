"""
    - Starting nodes to monitor:
        - S: The number of HHH nodes
        - 2**(l_0) <= S < 2**(l_0+1)
        - Nodes to monitor at level l_0: 
            - 2**(l_0) - (S-2**(l_0)) = 2**(l_0+1)-S
        - Nodes to monitor at level l_0 + 1: 
            - 2*(S - 2**(l_0))= 2S - 2**(l_0+1)    

    - Run Yu's algorithm, report HHH and calculate precision and recall. 
"""
import os
import sys
import math
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from tree_operation import parent, left_child, right_child, sibling
from metric import precision, recall

from yu_algo_main import yu_algo_main

class yu_algo(object):
    def __init__(self, S, threshold, leaf_level):
        """
            :param S: Number of HHHes
            :param num_of_TCAM: Number of TCAM entries used to monitor.
            :param threshold: HHH threshold.
            :param leaf_level: Leaf level of the tree.
        """
        self.S = S
        self.num_of_TCAM = 2*S + 2
        self.threshold = threshold
        self.leaf_level = leaf_level
    
        # Global parameter
        # :param time_interval: The index of current time interval.
        self.time_interval = 0

        # Find start nodes to monitor
        self.curr_nodes = self.find_start_nodes()
        self.rHHH_nodes = []

    def add_time_interval(self, M):
        """
            :param M: To alleviate randomness, aggregate over M unit time intervals
            to calculate average leaf_nodes.
        """
        self.time_interval += M

    def find_start_nodes(self):
        # Find start nodes to monitor
        S = self.S
        
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
            if node_l == self.leaf_level:
                # Leaf node
                curr_nodes.append(node)
            else:
                # Non-leaf node
                left_child_node, right_child_node = left_child(node, self.leaf_level), right_child(node, self.leaf_level)
                curr_nodes.append(left_child_node)
                curr_nodes.append(right_child_node)

        # Always monitor the root
        if (1,1) not in curr_nodes:
            curr_nodes.append((1,1))
        if (1,2) not in curr_nodes:
            curr_nodes.append((1,2))
        #print "Initial measuring nodes: ", curr_nodes
        return curr_nodes

    def run(self, leaf_nodes):
        """
            :param leaf_nodes: Leaf node counts at a time interval.
        """
        # Run yu's algorithm to calculate precision and recall. 
        rHHH_nodes, next_nodes = yu_algo_main(self.curr_nodes, leaf_nodes, self.leaf_level, self.threshold,self.num_of_TCAM)
        self.rHHH_nodes = rHHH_nodes
        self.curr_nodes = next_nodes

    def report(self, tHHH_nodes):
        """
            :returns: A report of results to be written to file.
        """
        results = []
        # Reported HHHes
        #print "reported HHHes: {0}".format(self.rHHH_nodes)
        line = "reporte HHHes: {0}\n".format(self.rHHH_nodes)
        results.append(line)

        # Calcualte precision and recall
        p = precision(self.rHHH_nodes, tHHH_nodes)
        r = recall(self.rHHH_nodes, tHHH_nodes)
        #print "At leaf_level = {0}, At time interval = {1}, precision: {2}, recall: {3}".format(self.leaf_level, self.time_interval, p, r)
        line = "At leaf_level = {0}, At time interval = {1}, precision: {2}, recall: {3}".format(self.leaf_level, self.time_interval, p, r)
        results.append(line)
        return results 


if __name__ == "__main__":
    main()
