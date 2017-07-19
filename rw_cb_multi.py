# Two pointers:
# Pointer p: current checking node
# Pointer q: current reading node
import sys
import math
import logging
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
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

# :param HHH_nodes: a list to store detected HHH's
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

def rw_cb_algo():
    global file_handler
    infile = "traffic_twoHHH.txt"
    ff = open(infile, 'rb')
    file_handler = ff

    # Initialize global parameters
    global time_interval, p_zero, error, threshold
    time_interval = 0
    #p_zero = p_init * 0.9

    # depth of the tree
    global levels
    L_depth = levels-1
    
    # Intermediate parameters 
    reading_node, checking_node = (0,1), (0,1)
    ns = node_status(checking_node, 0)
    ns_reading = node_status(reading_node, 0)
    
    # HHH nodes set
    global HHH_nodes
    HHH_nodes = {}
    while True:
        try:
            checking_level = checking_node[0]
            if checking_level == L_depth:
                """Leaf node."""
                # Observe the node until O_func outcome is 1 or 2
                # Until one of the equations holds
                O_func_outcome = 0
                while O_func_outcome == 0:
                    node_val = read(reading_node)
                    time_interval += 1
                    LOG.debug("At t={0}, node {1} val: {2}".format(time_interval, reading_node, node_val)) 
                    ns.x_mean = (ns.x_mean * ns.s + node_val) / float(ns.s + 1.0)
                    ns.s += 1.0

                    # Modify the node count by subtracting the time average count of 
                    # identified HHH descendants.
                    mod_x_mean = subtract_HHH(ns) 
                    LOG.debug("At t={0}, node {1} val: {2} after subtracting HHH's".format(time_interval, reading_node, mod_x_mean))
                    O_func_outcome = O_func(mod_x_mean, ns.s, threshold, p_zero, error)
                    
                if O_func_outcome == 1:
                    # Probably not an HHH, zoom out to parent node
                    checking_node = par(checking_node)
                    reading_node = checking_node
                    ns = node_status(checking_node, 0)
                    continue
                elif O_func_outcome == 2:
                    # Probably an HHH
                    #declare(checking_node)
                    HHH_nodes[checking_node] = ns
                    #print "Find HHH is {0} at time interval {1}".format(checking_node, time_interval)
                    LOG.debug("Find HHH is {0} at time interval {1}".format(checking_node, time_interval))

                    # Reset the pointer at the root node (l,k) = (0,1)
                    checking_node = (0,1)
                    reading_node = checking_node
                    ns = node_status(checking_node, 0)
                    continue
                else:
                    #print "Error: O_func_outcome can only be 1 or 2 after observation loop breaks"
                    LOG.error("Error: O_func_outcome can only be 1 or 2 after observation loop breaks.")

            elif checking_level < L_depth:
                """Not a leaf node."""
                # Observe the node until O_func outcome is 1 or 2
                # Until one of the equation holds
                O_func_outcome = 0
                if checking_level > 0:
                    while O_func_outcome == 0:
                        node_val = read(reading_node)
                        time_interval += 1
                        LOG.debug("At t={0}, node {1} val: {2}".format(time_interval, reading_node, node_val))
                        ns.x_mean = (ns.x_mean * ns.s + node_val) / float(ns.s+1.0)
                        ns.s += 1.0

                        # Modify the node count by subtracting the time average count of 
                        # identified HHH descendants.
                        mod_x_mean = subtract_HHH(ns)
                        LOG.debug("At t={0}, node {1} val: {2} after subtracting HHH's".format(time_interval, reading_node, mod_x_mean))
                        O_func_outcome = O_func(mod_x_mean, ns.s, threshold, p_zero, p_zero)
                elif checking_level == 0:
                    """Root node."""
                    while O_func_outcome == 0:
                        node_val = read(reading_node)
                        time_interval += 1
                        LOG.debug("At t={0}, node {1} val: {2}".format(time_interval, reading_node, node_val))
                        ns.x_mean = (ns.x_mean * ns.s + node_val) / float(ns.s+1.0)
                        ns.s += 1.0

                        # Modify the node count by subtracting the time average count of
                        # identified HHH descendants.
                        mod_x_mean = subtract_HHH(ns)
                        LOG.debug("At t={0}, node {1} val: {2} after subtracting HHH's".format(time_interval, reading_node, mod_x_mean))
                        O_func_outcome = O_func(mod_x_mean, ns.s, threshold, error, p_zero)
                else:
                    #print "Error: invalid node level."
                    LOG.error("Error: invalid node level.")

                if checking_level == 0:
                    """Root node."""
                    if O_func_outcome == 1:
                        ### DEBUG: 
                        #print "root node count: {0} and modified count: {1}".format(ns.x_mean, mod_x_mean)
                        LOG.debug("root node count: {0} and modified count: {1}".format(ns.x_mean, mod_x_mean))
                        # Probably no more HHHes remained to be detected
                        #print "At t = {0}, stop the search.".format(time_interval)
                        LOG.info("At t = {0}, stop the search.".format(time_interval))
                        output = ["node {0}".format(node_tag) for node_tag in HHH_nodes.keys()]
                        outstr = ','.join(output)
                        #print "t = {0}, ".format(time_interval) + outstr + " are HHH's"
                        LOG.info("t = {0}, ".format(time_interval) + outstr + " are HHH's")
                        break

                if O_func_outcome == 1:
                    # Praobably not an HHH, zoom out to parent node
                    checking_node = par(checking_node)
                    reading_node = checking_node
                    ns = node_status(checking_node, 0)
                    continue
                elif O_func_outcome == 2:
                    # Probably there exists an HHH under this prefix, zoom in
                    
                    # Observe left child until O_func outcome is 1 or 2
                    reading_node = left_child(checking_node)
                    O_func_outcome = 0
                    ns_reading = node_status(reading_node, 0)
                    while O_func_outcome == 0:
                        node_val = read(reading_node)
                        time_interval += 1
                        LOG.debug("At t={0}, node {1} val: {2}".format(time_interval, reading_node, node_val))
                        ns_reading.x_mean = (ns_reading.x_mean * ns_reading.s + node_val) / float(ns_reading.s+1.0)
                        ns_reading.s += 1.0

                        # Modify the node count by subtracting the time average count of 
                        # identified HHH descendants.
                        mod_x_mean = subtract_HHH(ns_reading)
                        LOG.debug("At t={0}, node {1} val: {2} after subtracting HHH's".format(time_interval, reading_node, mod_x_mean))
                        O_func_outcome = O_func(mod_x_mean, ns_reading.s, threshold, p_zero, p_zero)

                    if O_func_outcome == 2:
                        # Probably there exisits an HHH under this left child
                        # Move to left child
                        checking_node = left_child(checking_node)
                        reading_node = checking_node
                        ns = ns_reading
                        continue
                    elif O_func_outcome == 1:
                        # Probably left child not an HHH
                        # Observe right child until O_func outcome is 1 or 2
                        reading_node = right_child(checking_node)
                        O_func_outcome = 0
                        ns_reading = node_status(reading_node, 0)
                        while O_func_outcome == 0:
                            node_val = read(reading_node)
                            time_interval += 1
                            LOG.debug("At t={0}, node {1} val: {2}".format(time_interval, reading_node, node_val))
                            ns_reading.x_mean = (ns_reading.x_mean * ns_reading.s + node_val) / float(ns_reading.s+1.0)
                            ns_reading.s += 1.0

                            # Modify the node count by subtracting the time average count of
                            # identified HHH descendants.
                            mod_x_mean = subtract_HHH(ns_reading)
                            LOG.debug("At t={0}, node {1} val: {2} after subtracting HHH's".format(time_interval, reading_node, mod_x_mean))
                            O_func_outcome = O_func(mod_x_mean, ns_reading.s, threshold, p_zero, p_zero)

                        if O_func_outcome == 2:
                            # Probably there exists an HHH under this right child
                            # Move to right child
                            checking_node = right_child(checking_node)
                            reading_node = checking_node
                            ns = ns_reading
                            continue
                        elif O_func_outcome == 1:
                            # Probably right child not an HHH
                            # Neither left child nort right child an HHH, but current node probably an HHH
                            if p_zero < error:
                                #declare(checking_node)
                                HHH_nodes[checking_node] = ns
                                #print "Find HHH is {0} at time interval {1}".format(checking_node, time_interval)
                                LOG.debug("Find HHH is {0} at time interval {1}".format(checking_node, time_interval))
                                
                                # Reset the pointer to the root node (l,k) = (0,1)
                                checking_node = (0, 1)
                                reading_node = checking_node
                                ns = node_status(checking_node, 0)
                                continue
                            else:
                                reading_node = checking_node
                                p_zero /= 2.0
                                continue
                        else:
                            #print "Error: O_func_outcome can only be 1 or 2 after observation loop breaks"
                            LOG.error("Error: O_func_outcome can only be 1 or 2 after observation loop breaks.")
                    else:
                        #print "Error: O_func_outcome can only be 1 or 2 after observation loop breaks"
                        LOG.error("Error: O_func_outcome can only be 1 or 2 after observation loop breaks.")
        except EOFError:
            #print "End of file error occurred."
            LOG.error("Error: End of file error occurred.")
            break
    # Close traffic file
    ff.close()
        
if __name__ == "__main__":
    rw_cb_algo()
