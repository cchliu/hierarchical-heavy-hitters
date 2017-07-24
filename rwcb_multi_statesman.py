"""Capsulate rw_cb algorithm into a class.

    Run the algo like a state machine. 
"""
import sys
import math
import logging
from copy import deepcopy

from rwcb_multi_read import read_node, subtract_hhh, update_hhh_set

# Stucture for tracking node average
class node_status(object):
    def __init__(self, node, curr_s):
        self.node = node
        self.x_mean = 0
        self.s = curr_s


def O_func(x_mean, s, threshold, p1, p2, xi, logger):
    X_mean = x_mean
    curr_s = float(s)
    # Calculate the equation
    part1 = math.sqrt(2*xi*math.log(2*xi*curr_s**3/p1)/curr_s)
    equation_one = X_mean + part1
    if equation_one < threshold:
        logger.debug("X_mean: {0}, part1: {1}, threshold: {2}, return: {3}".format(X_mean, part1, threshold, 1))
        #print "X_mean: {0}, part1: {1}, threshold: {2}, return: {3}".format(X_mean, part1, threshold, 1)
        return 1

    part2 = math.sqrt(2*xi*math.log(2*xi*curr_s**3/p2)/curr_s)
    equation_two = X_mean - part2
    if equation_two > threshold:
        logger.debug("X_mean: {0}, part2: {1}, threshold:{2}, return: {3}".format(X_mean, part2, threshold, 2))
        #print "X_mean: {0}, part2: {1}, threshold: {2}, return: {3}".format(X_mean, part2, threshold, 2)
        return 2
    # Neither equ(1) or equ(2) holds
    return 0

# Find parent/left child/right child node along the tree
def par(node, root_level):
    node_level, node_k = node
    if node_level == root_level:
        return node
    par_node_level = node_level - 1
    par_node_k = (node_k + 1) / 2
    return (par_node_level, par_node_k)

def left_child(node, leaf_level):
    node_level, node_k = node
    if node_level == leaf_level:
        return None
    left_child_level = node_level + 1
    left_child_k = node_k*2 - 1
    return (left_child_level, left_child_k)

def right_child(node, leaf_level):
    node_level, node_k = node
    if node_level == leaf_level:
        return None
    right_child_level = node_level + 1
    right_child_k = node_k*2
    return (right_child_level, right_child_k)


class rwcb_algo(object):
    """Rewrite rwcb_multi algorithm as a state machine."""
    def __init__(self, threshold, p_zero, error, xi):
        # Logger
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

        # :param p_zero: initialize p_zero
        # :param threshold: HHH threshold
        # :param error
        # :param xi: parameter in equation (31) or (32)
        self.p_zero = p_zero
        self.threshold = threshold
        self.error = error
        self.xi = xi

        # :param time_interval: The index of current time interval.
        self.time_interval = 0

        # Parameters about the tree
        self.leaf_level = 0
        self.root_level, self.root_index = 0, 0
        
        # Initialize intermediate parameters
        self.reading_node = (0,1)
        self.checking_node = (0,1)
        self.ns = node_status(self.checking_node, 0)
        self.ns_reading = node_status(self.reading_node, 0)

    def _set_root_node(self, root_node):
        root_level, root_index = root_node
        self.root_level = root_level
        self.root_index = root_index

    def set_leaf_level(self, leaf_level):
        self.leaf_level = leaf_level

    def init_start_node(self, root_node):
        self._set_root_node(root_node)
        self.reading_node = root_node
        self.checking_node = root_node
        self.ns = node_status(self.checking_node, 0)
        self.ns_reading = node_status(self.reading_node, 0)

    def set_time_interval(self, val):
        self.time_interval = val

    def set_logging_level(self, level):
        self.logger.setLevel(level)

    def statesman(self, state, line, leaf_level, HHH_nodes):
        """Entry function.
        
            :param state: Next state, jump to corresponding function.
            :param line: Traffic count for all leaf nodes in the tree.
            :param leaf_level: The depth of the tree.
            :param HHH_nodes: The list of HHH nodes found up-to-now.
        """
        if state == "state_one":
            checking_level = self.checking_node[0]
            if checking_level == self.leaf_level:
                """Leaf node."""
                return self.state_one_leaf(line, leaf_level, HHH_nodes)
            elif checking_level < self.leaf_level:
                """Non-leaf node."""
                return self.state_one_nonleaf(line, leaf_level, HHH_nodes)
        elif state == "state_two":
            return self.state_two(line, leaf_level, HHH_nodes)
        elif state == "state_three":
            return self.state_three(line, leaf_level, HHH_nodes)

    def state_one_leaf(self, line, leaf_level, HHH_nodes):
        state_tag = "state_one_leaf"
        """Leaf node."""
        # Observe the node until O_func outcome is 1 or 2
        # Until one of the equations holds.
        node_val = read_node(self.reading_node, line, leaf_level)
        #time_interval += 1
        self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3}".format(state_tag, self.time_interval, self.reading_node, node_val))
        self.ns.x_mean = (self.ns.x_mean * self.ns.s + node_val) / float(self.ns.s + 1.0)
        self.ns.s += 1.0
        self.logger.debug("Stage = {0}: At t={1}, node {2}, mean: {3}, sample times: {4}".format(state_tag, self.time_interval, self.reading_node, self.ns.x_mean, self.ns.s))

        # Modify the node count by subtracting the time average count of
        # identified HHH descendants.
        mod_x_mean = subtract_hhh(self.ns, HHH_nodes)
        self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3} after subtracting HHH's".format(state_tag, self.time_interval, self.reading_node, mod_x_mean))
        O_func_outcome = O_func(mod_x_mean, self.ns.s, self.threshold, self.p_zero, self.error, self.xi, self.logger) 
        
        if O_func_outcome == 0:
            return "state_one"
        elif O_func_outcome == 1:
            # Probably not an HHH, zoom out to parent node
            self.checking_node = par(self.checking_node, self.root_level)
            self.reading_node = self.checking_node          
            self.ns = node_status(self.checking_node, 0)
            return "state_one"
        elif O_func_outcome == 2:
            # Probably an HHH
            update_hhh_set(self.ns, HHH_nodes)
            self.logger.info("Find HHH {0} at time interval {1}".format(self.checking_node, self.time_interval))
            
            # Reset the pointer at the root node of subtree (l,k) = (0, 1)
            self.checking_node = (self.root_level, self.root_index)
            self.reading_node = self.checking_node
            self.ns = node_status(self.checking_node, 0)
            return "state_one"
        else:
            self.logger.error("Error: O_func_outcome can only be 1 or 2 after observation loop breaks.")            

    def state_one_nonleaf(self, line, leaf_level, HHH_nodes):
        state_tag = "state_one_nonleaf"
        """Not a leaf node."""
        # Observe the node until O_func outcome is 1 or 2
        # Until one of the equation holds
        node_val = read_node(self.reading_node, line, leaf_level)
        #time_interval += 1
        self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3}".format(state_tag, self.time_interval, self.reading_node, node_val))
        self.ns.x_mean = (self.ns.x_mean * self.ns.s + node_val) / float(self.ns.s + 1.0)
        self.ns.s += 1.0
        self.logger.debug("Stage = {0}: At t={1}, node {2}, mean: {3}, sample times: {4}".format(state_tag, self.time_interval, self.reading_node, self.ns.x_mean, self.ns.s))

        # Modify the node count by subtracting the time average count of
        # identified HHH descendants.
        mod_x_mean = subtract_hhh(self.ns, HHH_nodes)
        self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3} after subtracting HHH's".format(state_tag, self.time_interval, self.reading_node, mod_x_mean))

        checking_level = self.checking_node[0]
        if checking_level > self.root_level:
            O_func_outcome = O_func(mod_x_mean, self.ns.s, self.threshold, self.p_zero, self.p_zero, self.xi, self.logger)
        elif checking_level == self.root_level:
            """Root node."""
            O_func_outcome = O_func(mod_x_mean, self.ns.s, self.threshold, self.error, self.p_zero, self.xi, self.logger)
        else:
            self.logger.error("Error: invalid node level.")

        if O_func_outcome == 0:
            return "state_one"
        if checking_level == self.root_level:
            """Root node."""
            if O_func_outcome == 1:
                self.logger.info("At t = {0}, stop the search.".format(self.time_interval))
                return "break"
        if O_func_outcome == 1:
            # Probably not an HHH, zoom out to parent node
            self.checking_node = par(self.checking_node, self.root_level)
            self.reading_node = self.checking_node
            self.ns = node_status(self.checking_node, 0)
            return "state_one"
        elif O_func_outcome == 2:
            # Probably there exists an HHH under this prefix, zoom in
            # Observe left child in the next time interval
            self.reading_node = left_child(self.checking_node, self.leaf_level)
            self.ns_reading = node_status(self.reading_node, 0)
            return "state_two"

    def state_two(self, line, leaf_level, HHH_nodes):
        state_tag = "state_two"
        # Observe left child until O_func outcome is 1 or 2
        node_val = read_node(self.reading_node, line, leaf_level)
        #time_interval += 1
        self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3}".format(state_tag, self.time_interval, self.reading_node, node_val))
        self.ns_reading.x_mean = (self.ns_reading.x_mean * self.ns_reading.s + node_val) / float(self.ns_reading.s + 1.0)
        self.ns_reading.s += 1.0
        self.logger.debug("Stage = {0}: At t={1}, node {2}, mean: {3}, sample times: {4}".format(state_tag, self.time_interval, self.reading_node, self.ns_reading.x_mean, self.ns_reading.s))

        # Modify the node count by subtracting the time average count of 
        # identified HHH descendants.
        mod_x_mean = subtract_hhh(self.ns_reading, HHH_nodes)
        self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3} after subtracting HHH's".format(state_tag, self.time_interval, self.reading_node, mod_x_mean))

        O_func_outcome = O_func(mod_x_mean, self.ns_reading.s, self.threshold, self.p_zero, self.p_zero, self.xi, self.logger)
        if O_func_outcome == 0:
            return "state_two" 
        elif O_func_outcome == 2:
            # Probably there exisits an HHH under this left child
            # Move to the left child
            self.checking_node = left_child(self.checking_node, self.leaf_level)
            self.reading_node = self.checking_node
            self.ns = self.ns_reading
            return "state_one"
        elif O_func_outcome == 1:
            # Probably left child not an HHH
            # Observe right child in the next time interval
            self.reading_node = right_child(self.checking_node, self.leaf_level)
            self.ns_reading = node_status(self.reading_node, 0)
            return "state_three"

    def state_three(self, line, leaf_level, HHH_nodes):
            state_tag = "state_three"
            # Probably left child not an HHH
            # Observe right child until O_func outcome is 1 or 2
            node_val = read_node(self.reading_node, line, leaf_level)
            #time_interval += 1
            self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3}".format(state_tag, self.time_interval, self.reading_node, node_val))
            self.ns_reading.x_mean = (self.ns_reading.x_mean * self.ns_reading.s + node_val) / float(self.ns_reading.s + 1.0)
            self.ns_reading.s += 1.0
            self.logger.debug("Stage = {0}: At t={1}, node {2}, mean: {3}, sample times: {4}".format(state_tag, self.time_interval, self.reading_node, self.ns_reading.x_mean, self.ns_reading.s))
            # Modify the node count by subtracting the time average count of
            # identified HHH descendants
            mod_x_mean = subtract_hhh(self.ns_reading, HHH_nodes)
            self.logger.debug("Stage = {0}: At t={1}, node {2} val: {3} after subtracting HHH's".format(state_tag, self.time_interval, self.reading_node, mod_x_mean))

            O_func_outcome = O_func(mod_x_mean, self.ns_reading.s, self.threshold, self.p_zero, self.p_zero, self.xi, self.logger)

            if O_func_outcome == 0:
                return "state_three"
            elif O_func_outcome == 2:
                # Probably there exisits an HHH under right child
                # Move to right child
                self.checking_node = right_child(self.checking_node, self.leaf_level)
                self.reading_node = self.checking_node
                self.ns = self.ns_reading
                return "state_one"
            elif O_func_outcome == 1:
                # Probably right child not an HHH
                # Neither left child nor right child an HHH, but current node probably an HHH
                if self.p_zero < self.error:
                    update_hhh_set(self.ns, HHH_nodes)
                    self.logger.info("Find HHH {0} at time interval {1}".format(self.checking_node, self.time_interval))

                    # Reset the pointer to the root node (l,k) = (0,1)
                    if self.checking_node != (self.root_level, self.root_index):
                        self.checking_node = (self.root_level, self.root_index)
                        self.ns = node_status(self.checking_node, 0)
                    else:
                        self.ns = deepcopy(self.ns)
                    self.reading_node = self.checking_node
                    return "state_one"
                else:
                    self.reading_node = self.checking_node
                    self.p_zero /= 2.0
                    self.logger.debug("At t={0}, checking node {1}, p_zero: {2}".format(self.time_interval, self.checking_node, self.p_zero))
                    return "state_one"
            else:
                self.logger.error("Error: O_func_outcome can only be 1 or 2 after observation loop breaks.")


