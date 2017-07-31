"""
    Package parallel rwcb algorithm into a class.

    Divid into subtrees.
    - :param S: Number of HHH nodes.
    - :param N: Number of counters.
    - N = num_of_TCAM = 2*S + 2, same as the settings in Yu's algorithm.
    - :param M: M = N-S
        - 2**l0 <= M < 2**(l0+1)
        - Subtrees with root node on level l0:
            - 2**l0 - (M-2**l0) = 2**(l0+1) - M
        - Subtrees with root node on level l1:
            - 2*(M - 2**l0) = 2M - 2**(l0+1)

    Search all subtrees to find HHHes at lower levels.

    After finishing searching all subtrees, start from the root node
    to search for HHH's on topper levels.
"""
import os
import sys
import math
import logging
module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'module')
sys.path.append(module_path)

from rwcb_multi_statesman_ht import rwcb_algo
from rwcb_multi_hhh import update_hhh_count
from metric import precision, recall

class parallel_rwcb_algo(object):
    def __init__(self, leaf_level, threshold, p_zero, error, b, u, S, logging_level):
        """
            :param leaf_lambdas: distribution parameters to generate synthetic traces.
                - A list of [(l,k), val]
            :param leaf_level: Leaf level.

            :param threshold: HHH threshold.
            :param b: parameter in equation (31) and (32).
            :param u: parameter in equation (31) and (32)
            :param p_zero: initial p_zero.

            :param S: The number of HHH's.
            :param N: The number of counters.
        """
        #self.leaf_lambdas = leaf_lambdas
        self.leaf_level = leaf_level
 
        self.threshold = threshold
        self.b = b
        self.u = u
        self.error = error
        self.p_zero = p_zero
       
        self.S = S
        self.N = 2*self.S + 2
 
        # Logger
        self.logging_level = logging_level

        # parallel rwcb algo global variables.
        # :param time_interval: The index of current time interval.
        self.time_interval = 0

        # :param HHH_nodes: a list to store detected HHH's
        # key: (l, k), value: :class:`node_status'
        self.HHH_nodes = {}
        
        # Divide into subtrees
        self.divide_subtrees()

        # Create the top level search tree object
        self.create_topts()

    def divide_subtrees(self):
        """Divide into subtrees."""
        # :param N: The number of counters
        # :param S: The number of HHH's
        S = self.S
        N = self.N
        M = N - S
        # 2^l0 <= M < 2^(l0+1)
        l0 = int(math.log(M, 2))
        l1 = l0 + 1
        # :param n0: Number of subtrees with roots on level l0
        # :param n1: Number of subtrees with roots on level l1
        n1 = 2*(M - 2**l0)
        n0 = 2**(l1) - M

        # A list of subtree search objects
        # And its corresponding states
        subts, states = [], []
        for i in range(M):
            if i < n0:
                root_node = (l0, i+1)
            else:
                root_node = (l1, n0+i+1)

            # Instantiate subtree search object
            ts = rwcb_algo(self.threshold, self.p_zero, self.error, self.b, self.u)
            ts.set_leaf_level(self.leaf_level)
            ts.init_start_node(root_node)
            ts.set_scale_const(self.S)
            ts.set_logging_level(self.logging_level)
            subts.append(ts)
            states.append("state_one")

        self.subts = subts
        self.states = states

    def create_topts(self):
        # Search HHHes at the top level.
        root_node = (0,1)
        ts = rwcb_algo(self.threshold, self.p_zero, self.error, self.b, self.u)
        ts.set_leaf_level(self.leaf_level)
        ts.init_start_node(root_node)
        ts.set_scale_const(self.S)
        ts.set_logging_level(self.logging_level)
        self.topts = ts
        self.top_state = "state_one"
       
    def run(self, leaf_nodes):
        num_of_subts = len(self.subts)
        next_subts, next_states = [], []
        if num_of_subts:
            # Search HHHes under subtrees.
            # Not all subtrees finish searching.
            self.time_interval += 1
            update_hhh_count(leaf_nodes, self.HHH_nodes)
            for idx, ts in enumerate(self.subts):
                ts.set_time_interval(self.time_interval)
                state = self.states[idx]
                state = ts.statesman(state, leaf_nodes, self.leaf_level, self.HHH_nodes)
                if not state == "break":
                    next_subts.append(ts)
                    next_states.append(state) 

            self.subts = next_subts
            self.states = next_states
        else:
            # All subtrees finish searching.
            # Search HHHes at the top level.
            self.time_interval += 1
            update_hhh_count(leaf_nodes, self.HHH_nodes)
            self.topts.set_time_interval(self.time_interval)
            state = self.top_state
            self.top_state = self.topts.statesman(state, leaf_nodes, self.leaf_level, self.HHH_nodes)
            if self.top_state == "break":
                return 1 
        return 0

    def report(self, tHHH_nodes):
        results = []
        rHHH_nodes = self.HHH_nodes.keys()
        rHHH_nodes = sorted(rHHH_nodes, key = lambda x:x[0])
        #print "reported HHHes: ", rHHH_nodes
        line = "reported HHHes: {0}".format(rHHH_nodes)
        results.append(line)
    
        # Calculate precision and recall
        p = precision(rHHH_nodes, tHHH_nodes)
        r = recall(rHHH_nodes, tHHH_nodes)
        #print "At leaf_level = {0}, error = {1}, at time = {2}, stop the search. precision: {3}, recall: {4}".format(self.leaf_level, self.error, self.time_interval, p, r)
        line = "At leaf_level = {0}, error = {1}, xi = {2}, at time = {3}, stop the search. precision: {4}, recall: {5}".format(self.leaf_level, self.error, self.xi, self.time_interval, p, r)
        results.append(line)
        return results
     

if __name__ == "__main__":
    iterations = 1000
    for i in range(iterations):
        run()
