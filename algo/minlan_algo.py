"""
    - Starting nodes to monitor:
        - S: The number of HHH nodes
        - 2**(l_0) <= S < 2**(l_0+1)
        - Nodes to monitor at level l_0: 
            - 2**(l_0) - (S-2**(l_0)) = 2**(l_0+1)-S
        - Nodes to monitor at level l_0 + 1: 
            - 2*(S - 2**(l_0))= 2S - 2**(l_0+1)    

    - Monitor a node by installing rules for its two children.

    - In total we use 2 + 2/T TCAM entries.

    - Run Yu's algorithm, report HHH and calculate precision and recall. 
"""
import sys
import logging
import math

_EARLY_LOG_HANDLER = logging.StreamHandler(sys.stderr)
log = logging.getLogger()
if not len(log.handlers):
    log.addHandler(_EARLY_LOG_HANDLER)

from module.offline_caida import Node

from tree_operations import get_parent, get_left_child, get_right_child, get_sibling
from tree_operations import read

class MinlanAlgo(object):
    def __init__(self, leaf_level, threshold, S, logging_level):
        """
            :param S: Number of HHHes
            :param threshold: HHH threshold.
            :param leaf_level: Leaf level of the tree.
        """
        self.S = S
        self.num_of_TCAM = 2*S + 2
        self.threshold = threshold
        self.leaf_level = leaf_level

        # :param time_interval: The index of current time interval.
        self.time_interval = 0

        # Logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)

        # Find start nodes to monitor
        # prefixes: prefixes we monitor
        # children: install rules to monitor the prefixes' children
        self.prefixes = []
        self.children = []
        self.find_start_nodes()
        self.mHHH = []


    def find_start_nodes(self):
        # Find start nodes to monitor
        S = self.S

        l0 = int(math.log(S, 2))
        l0_num = 2**(l0+1) - S
        l1_num = 2*S - 2**(l0+1)

        curr_monitors = []
        for i in range(l0_num):
            node = (l0, i)
            curr_monitors.append(node)

        for i in range(l0_num, 2**l0):
            node = (l0+1, i*2)
            curr_monitors.append(node)
            node = (l0+1, i*2+1)
            curr_monitors.append(node)
        curr_monitors = set(curr_monitors)
        curr_monitors.add((0,0))
        self.prefixes = list(curr_monitors)
        self.logger.debug("At t=%d, monitoring prefixes: %s", self.time_interval+1, \
                ','.join(str(k) for k in sorted(self.prefixes, key = lambda x:x[0], reverse=True)))

        # Find start nodes to measure
        children = set()
        for node in curr_monitors:
            node_l, node_k = node
            if node_l == self.leaf_level:
                # Leaf node
                children.add(node)
            else:
                # Non-leaf node
                children.add(get_left_child(node_l, node_k, self.leaf_level))
                children.add(get_right_child(node_l, node_k, self.leaf_level))

        # Always monitor the root
        node = (1,0)
        children.add(node)
        node = (1,1)
        children.add(node)
        self.children = list(children)
        self.children = sorted(self.children, key = lambda x:x[0], reverse=True)
        self.logger.debug("Initial install rules at nodes: %s", ','.join(str(k) for k in children))
        


    def run(self, dvalues):
        """Function called at each time interval to find reported/measured HHHes.
        """
        self.time_interval += 1
        #self.logger.debug("At t=%d, leaf node values: %s", self.time_interval, \
        #        ','.join(str(k)+':'+str(v)+' ' for k,v in sorted(dvalues.items(), key = lambda x:x[0][1])))

        # Read aggregated counters from installed rules.
        curr_vals = {}
        for (l,k) in self.children:
            curr_vals[(l,k)] = read(l, k, dvalues)
        self.logger.debug("At t=%d, threshold = %f, aggregated values of rules: %s", self.time_interval, self.threshold, \
                ','.join(str(k)+':'+str(v)+' ' for k,v in sorted(curr_vals.items(), key = lambda x:x[0][0], reverse=True)))

        # Process the counts as TCAM entries, the same packet won't count twice.
        sorted_nodes = sorted(curr_vals.keys(), key = lambda x:x[0], reverse=True)
        for node in sorted_nodes:
            val = curr_vals[node]
            l, k = node
            pl, pk = l-1, k/2
            while pl >= 0:
                if (pl, pk) in curr_vals:
                    curr_vals[(pl, pk)] -= val
                pl, pk = pl-1, pk/2
        self.logger.debug("At t=%d, threshold = %f, values of rules: %s", self.time_interval, self.threshold, \
                ','.join(str(k)+':'+str(v)+' ' for k,v in sorted(curr_vals.items(), key = lambda x:x[0][0], reverse=True)))

        # Find reported HHHes
        mHHH = []
        mHHH_tags = set()
        # If node count of node p is below the threshold, we add p's count to the 
        # nearest upstream prefix in the TCAM.
        for (l,k) in sorted(self.prefixes, key = lambda x:x[0], reverse=True):
            val = 0
            if l == self.leaf_level:
                # If leaf node
                val = curr_vals[(l,k)]
                if val > self.threshold and not (l,k) in mHHH_tags:
                    newNode = Node(l, k, val)
                    mHHH.append(newNode)
                    mHHH_tags.add((l,k))
                    curr_vals[(l,k)] = 0
                else:
                    pl, pk = l-1, k/2
                    while pl>=0:
                        if (pl, pk) in self.children:
                            curr_vals[(pl, pk)] += val
                            break
                        pl, pk = pl-1, pk/2

            else:
                # It is possible that the number of reported HHHes are larger than Smax
                # therefore some reported HHHes don't have enought counters to monitor
                # their children.

                # If non-leaf node
                left_child = get_left_child(l, k, self.leaf_level)
                if not left_child in curr_vals:
                    continue
                left_val = curr_vals[left_child] if left_child else 0
                if left_val > self.threshold:
                    if not left_child in mHHH_tags:
                        newNode = Node(left_child[0], left_child[1], left_val)
                        mHHH.append(newNode)
                        mHHH_tags.add(left_child)
                else:
                    val += left_val

                right_child = get_right_child(l, k, self.leaf_level)
                if not right_child in curr_vals:
                    continue
                right_val = curr_vals[right_child] if right_child else 0
                if right_val > self.threshold:
                    if not right_child in mHHH_tags:
                        newNode = Node(right_child[0], right_child[1], right_val)
                        mHHH.append(newNode)
                        mHHH_tags.add(right_child)
                else:
                    val += right_val
            
                if val > self.threshold:
                    if not (l,k) in mHHH_tags:
                        newNode = Node(l, k, val)
                        mHHH.append(newNode)
                        mHHH_tags.add((l,k))
                    curr_vals[(l,k)] = 0
                else:
                    curr_vals[(l,k)] = val
                    pl, pk = l-1, k/2
                    if not (pl,pk) in self.prefixes:
                        while pl >=0:
                            if (pl, pk) in self.children:
                                curr_vals[(pl, pk)] += val
                                break
                            pl, pk = pl-1, pk/2

        self.logger.info('Reported HHHes: %s', ', '.join(str((node.l, node.k))+': '+str(node.val) for node in sorted(mHHH, key=lambda x:x.l, reverse=True)))
        
        # Prepare rules for next time interval
        self.prefixes = set([(node.l, node.k) for node in mHHH])
        self.prefixes.add((0,0))
	children = set()

        # Always monitor the root
        node = (1,0)
        children.add(node)
        node = (1,1)
        children.add(node)

	# Monitor children of reported HHHes
        for node in sorted(mHHH, key=lambda x:x.val, reverse=True):
            l, k = node.l, node.k
            if l == self.leaf_level:
                # Leaf node
                children.add((l,k))
                if len(children) == self.num_of_TCAM:
                    break
            else:
                children.add(get_left_child(l, k, self.leaf_level))
                if len(children) == self.num_of_TCAM:
	            break	
                children.add(get_right_child(l, k, self.leaf_level))
                if len(children) == self.num_of_TCAM:
                    break

        # If there are spare entries
        if len(children) < self.num_of_TCAM:
            # Sort existing HHHes in increasing order
            sorted_hhh_nodes = sorted(mHHH, key = lambda x:x.val)

            # Use spare rules to monitor the parents of existing HHHes
            # We install rules to monitor these HHHes' siblings.
            for node in sorted_hhh_nodes:
                sibling_node = get_sibling(node.l, node.k)
                if sibling_node:
                    children.add(sibling_node)
                    self.prefixes.add(get_parent(node.l, node.k))
                    if len(children) == self.num_of_TCAM:
                        break

        self.children = list(children)
        self.prefixes = list(self.prefixes)
        self.logger.debug("At t=%d, monitoring prefixes: %s", self.time_interval+1, \
                ','.join(str(k) for k in sorted(self.prefixes, key = lambda x:x[0], reverse=True)))
        self.logger.debug("At t=%d, TCAM num: %d, used num: %d, installing rules at nodes: %s", \
                self.time_interval+1, self.num_of_TCAM, len(self.children), \
                ','.join(str(k) for k in sorted(self.children, key = lambda x:x[0], reverse=True)))
        return mHHH
