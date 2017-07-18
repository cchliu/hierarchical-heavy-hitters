# Two pointers:
# Pointer p: current checking node
# Pointer q: current reading node
import sys
import math
import logging
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# :param time_interval: the index of current time interval
# :param file_handler: file object to read traffic data from
# :param levels: the depth of tree 
global time_interval, file_handler, levels
levels = 4

# :param threshold: HHH threshold
# :param epsno: parameter in equation (31) or (32)
# :param p_zero: initialize p_zero
global threshold, xi, p_zero, error
p_init = 1 - 1.0 / (2**(1.0/3.0))
p_zero = p_init * 0.9
error = p_init * 0.5
xi = 3.0
threshold = 25

# Stucture for tracking node average
class node_status(object):
    def __init__(self, node, curr_s):
        self.node = node
        self.x_mean = 0
        self.s = curr_s

# :param HHH_nodes: a list to store HHH's detected
global HHH_nodes
# key: (l, k), value: :class:`node_status' 
HHH_nodes = {}
#---------------------------------------#
"""Setup global parameters before running the algo.

    :param threshold: HHH threshold.
    :param epsno: parameter in equation (31) or (32).
    :param levels: The depth of tree.
    :param p_zero: Initialize p_zero.
    :param error: Error 
"""
def setup_params_error(val):
    global error
    error = val

def setup_params_xi(val):
    global xi
    xi = val

def setup_params_pzero(val):
    global p_zero
    p_zero = val

def print_params():
    global error, xi, threshold, p_zero
    print "Error: {0}, Threshold: {1}, Xi: {2}, p_zero initialized to {3}".format(error, threshold, xi, p_zero)
#---------------------------------------#

def subtract_HHH(ns):
    """Modify the count of node by substracting the count 
    of its HHH decendants."""
    global HHH_nodes
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
        
    
def update_count_HHH(line):
    """If the HHH_nodes set are not empty, for each identified HHH_node,
    keep counting the sample mean of it."""
    global HHH_nodes, levels
    for node in HHH_nodes.keys():
        node_level, node_k = node
        node_val = 0
        for idx, val in enumerate(line):
            curr_level = levels - 1
            curr_k = idx + 1
            while(curr_level >= node_level):
                if node == (curr_level, curr_k):
                    node_val += val
                curr_level -= 1
                curr_k = (curr_k + 1) /2
        ns = HHH_nodes[node]
        ns.x_mean = (ns.x_mean * ns.s + node_val) / float(ns.s + 1.0)
        ns.s += 1.0

def read(node):
    """Read traffic data of node at the current time_interval.
    
    If the HHH_nodes set are not empty, for each identified HHH_node,
    keep counting the sample mean of it.

    If the HHH_nodes set are not empty, the sample mean of all the parents 
    of an HHH_node is modified by subtracting the sample mean of this HHH_node.

        :param node: The node whose value to read.
    """
    global file_handler, levels
    ff = file_handler
    line = ff.readline().rstrip('\n')
    if not line:
        raise EOFError 
    line = [int(k) for k in line.split(',')]
    
    # update time average count for HHH_nodes
    update_count_HHH(line)

    node_val = 0
    node_level, node_k = node
    for idx, val in enumerate(line):
        curr_level = levels-1
        curr_k = idx + 1
        while(curr_level >= node_level):
            if node == (curr_level, curr_k):
                node_val += val
            curr_level -= 1
            curr_k = (curr_k + 1) / 2
    return node_val

def O_func(x_mean, s, threshold, p1, p2):
    global xi 
    X_mean = x_mean
    curr_s = float(s)
    # Calculate the equation
    equation_one = X_mean + math.sqrt(2*xi*math.log(2*xi*curr_s**3/p1)/curr_s)
    if equation_one < threshold:
        return 1
    equation_two = X_mean - math.sqrt(2*xi*math.log(2*xi*curr_s**3/p2)/curr_s)
    if equation_two > threshold:
        return 2
    # Neither equ(1) or equ(2) holds
    return 0

# Find parent/left child/right child node along the tree
def par(node):
    node_level, node_k = node
    if node_level == 0:
        return node
    par_node_level = node_level - 1
    par_node_k = (node_k + 1) / 2
    return (par_node_level, par_node_k)

def left_child(node):
    node_level, node_k = node
    if node_level == levels - 1:
        return None
    left_child_level = node_level + 1
    left_child_k = node_k*2 - 1
    return (left_child_level, left_child_k)

def right_child(node):
    node_level, node_k = node
    if node_level == levels - 1:
        return None
    right_child_level = node_level + 1
    right_child_k = node_k*2
    return (right_child_level, right_child_k)


class rwcb_algo(object):
    """Rewrite rwcb_multi algorithm as a state machine."""
    def __init__(self, threshold, p_zero, error):
        # Logger
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

        # :param p_zero: initialize p_zero
        p_init = 1 - 1.0 / (2**(1.0/3.0))
        self.p_zero = p_init * 0.9

        # Parameters about the tree
        self.leaf_level = 0
        self.root_level, self.root_index = 0, 0
        
        # Initialize intermediate parameters
        self.reading_node = (0,1)
        self.checking_node = (0,1)
        self.ns = node_status(self.checking_node, 0)
        self.ns_reading = node_status(self.reading_node, 0)

    def set_root_node(self, root_node):
        root_level, root_index = root_node
        self.root_level = root_level
        self.root_index = root_index

    def set_leaf_level(self, leaf_level):
        self.leaf_level = leaf_level

    def init_start_node(self):
        self.reading_node = (self.root_level, self.root_index)
        self.checking_node = (self.root_level, self.root_index)
        self.ns = node_status(self.checking_node, 0)
        self.ns_reading = ndoe_status(self.reading_node, 0)

    def statesman(self, state):
        if state == "state_one":
            checking_level = self.checking_node[0]
            if checking_level == self.leaf_level:
                return self.state_one_leaf()

    def state_one_leaf(self):
        state_tag = "state_one_leaf"
        """Leaf node."""
        # Observe the node until O_func outcome is 1 or 2
        # Until one of the equations holds.
        node_val = read(self.reading_node)
        #time_interval += 1
        self.ns.x_mean = (self.ns.x_mean * self.ns.s + node_val) / float(self.ns.s + 1.0)
        self.ns.s += 1.0

        # Modify the node count by subtracting the time average count of
        # identified HHH descendants.
        mod_x_mean = subtract_HHH(self.ns)
        O_func_outcome = O_func(mod_x_mean, self.ns.s, threshold, self.p_zero, error) 
        
        if O_func_outcome == 0:
            return "state_one_leaf"
        elif O_func_outcome == 1:
            # Probably not an HHH, zoom out to parent node
            self.checking_node = par(self.checking_node)
            self.reading_node = self.checking_node            
            self.ns = node_status(self.checking_node, 0)
            return "state_one_leaf"
        elif O_func_outcome == 2:
            # Probably an HHH
            update_hhh_set(self.ns)
            
            # Reset the pointer at the root node of subtree (l,k) = (0, 1)
            self.checking_node = (self.root_level, self.root_index)
            self.reading_node = self.checking_node
            self.ns = node_status(self.checking_node, 0)
            return "state_one_leaf"
        else:
            self.logger.error("Error: O_func_outcome can only be 1 or 2 after observation loop breaks.")            

    def state_one_nonleaf(self):
        state_tag = "state_one_nonleaf"
        """Not a leaf node."""
        # Observe the node until O_func outcome is 1 or 2
        # Until one of the equation holds
        node_val = read(self.reading_node)
        time_interval += 1
        self.ns.x_mean = (self.ns.x_mean * self.ns.s + node_val) / float(self.ns.s + 1.0)
        self.ns.s += 1.0

        # Modify the node count by subtracting the time average count of
        # identified HHH descendants.
        mod_x_mean = subtract_HHH(self.ns)
        
        checking_level = self.checking_node[0]
        if checking_level > self.root_level:
            O_func_outcome = O_func(mod_x_mean, self.ns.s, threshold, p_zero, p_zero)
        elif checking_level == self.root_level:
            """Root node."""
            O_func_outcome = O_func(mod_x_mean, self.ns.s, threshold, error, p_zero)
        else:
            self.logger.error("Error: invalid node level.")

        if checking_level == self.root_level:
            """Root node."""
            if O_func_outcome == 1:
                self.logger.info("At t = {0}, stop the search.".format(time_interval)
                output = ["node {0}".format(node_tag) for node_tag in HHH_nodes.keys()]
                outstr = ','.join(output)
                self.logger.info("t = {0}, ".format(time_interval) + outstr + " are HHH's")
                return "break"
        if O_func_outcome == 1:
            # Probably not an HHH, zoom out to parent node
            self.checking_node = par(self.checking_node)
            self.reading_node = self.checking_node
            self.ns = node_status(self.checking_node, 0)
            return "state_one_nonleaf"
        elif O_func_outcome == 2:
            # Probably there exists an HHH under this prefix, zoom in
            self.state_two_nonleaf()

    def state_two_nonleaf(self):
        # Observe left child until O_func outcome is 1 or 2
        self.reading_node = left_child(self.checking_node)
        self.ns_reading = node_status(self.reading_node, 0)
        node_val = read(self.reading_node)
        time_interval += 1
        self.ns_reading.x_mean = (self.ns_reading.x_mean * self.ns_reading.s + node_val) / float(self.ns_reading.s + 1.0)
        self.ns_reading.s += 1.0

        # Modify the node count by subtracting the time average count of 
        # identified HHH descendants.
        mod_x_mean = subtract_HHH(self.ns_reading)
        O_func_outcome = O_func(mod_x_mean, self.ns_reading.s, threshold, p_zero, p_zero)
        if O_func_outcome == 2:
            # Probably there exisits an HHH under this left child
            # Move the left child
            self.checking_node = left_child(self.checking_node)
            self.reading_node = self.checking_node
            self.ns = self.ns_reading
            return "state_one"
        elif O_func_outcome == 1:
            return state_three_nonleaf

    def state_three_nonleaf(self):
            # Probably left child not an HHH
            # Observe right child until O_func outcome is 1 or 2
            self.reading_node = right_child(self.checking_node)
            node_val = read(self.reading_node)
            time_interval += 1
            self.ns_reading.x_mean = (self.ns_reading.x_mean * self.ns_reading.s + node_val) / float(self.ns_reading.s + 1.0)
            self.ns_reading.s += 1.0

            # Modify the node count by subtracting the time average count of
            # identified HHH descendants
            mod_x_mean = subtract_HHH(self.ns_reading)
            O_func_outcome = O_func(mod_x_mean, self.ns_reading.s, threshold, p_zero, p_zero)

            if O_func_outcome == 2:
                # Probably there exisits an HHH under right child
                # Move to right child
                self.checking_node = right_child(self.checking_node)
                self.reading_node = self.checking_node
                self.ns = self.ns_reading
                return "state_one_nonleaf"
            elif O_func_outcome == 1:
                # Probably right child not an HHH
                # Neither left child nor right child an HHH, but current node probably an HHH
                if p_zero < error:
                    update_hhh_set(self.checking_node, self.ns)
                    self.logger.debug("Find an HHH {0} at time interval {1}".format(self.checking_node, time_interval))

                    # Reset the pointer to the root node (l,k) = (0,1)
                    self.checking_node = (self.root_level, self.root_index)
                    self.reading_node = self.checking_node
                    self.ns = node_status(self.checking_node, 0)
                else:
                    p_zero /= 2.0
            else:
                self.logger.error("Error: O_func_outcome can only be 1 or 2 after observation loop breaks.")


if __name__ == "__main__":
    rw_cb_algo()
