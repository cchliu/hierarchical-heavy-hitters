# Two pointers:
# Pointer p: current checking node
# Pointer q: current reading node
import math

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
error = p_init * 0.5
xi = 1.0
threshold = 25

# Stucture for current checking node
class node_status(object):
    def __init__(self, node, curr_s):
        self.node = node
        self.x_mean = 0
        self.s = curr_s
 
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

def print_params():
    global error, threshold
    print "Error: {0}, Threshold: {1}".format(error, threshold)
#---------------------------------------#

def read(node):
    """Read traffic data of node at the current time_interval.

        :param node: The node whose value to read.
        :param time_interval: The current time interval.
    """
    global file_handler, levels
    ff = file_handler
    line = ff.readline().rstrip('\n')
    if not line:
        raise EOFError 
    line = [int(k) for k in line.split(',')]
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
    equation_one = X_mean + math.sqrt(2*xi*math.log(2*xi*curr_s**3/p1, 2)/curr_s)
    if equation_one < threshold:
        return 1
    equation_two = X_mean - math.sqrt(2*xi*math.log(2*xi*curr_s**3/p2, 2)/curr_s)
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
    infile = "traffic.txt"
    ff = open(infile, 'rb')
    file_handler = ff

    # Initialize global parameters
    global time_interval, p_zero, error, threshold
    time_interval = 0
    p_zero = p_init * 0.9
    reading_node, checking_node = (0,1), (0,1)
    ns = node_status(checking_node, 0)
    ns_reading = node_status(reading_node, 0)
    # depth of the tree
    global levels
    L_depth = levels-1
    while True:
        try:
            checking_level = checking_node[0]
            if checking_level == L_depth:
                # Observe the node until O_func outcome is 1 or 2
                # Until one of the equations holds
                O_func_outcome = 0
                while O_func_outcome == 0:
                    node_val = read(reading_node)
                    time_interval += 1
                    ns.x_mean = (ns.x_mean * ns.s + node_val) / float(ns.s + 1.0)
                    ns.s += 1.0
                    O_func_outcome = O_func(ns.x_mean, ns.s, threshold, p_zero, error)
                if O_func_outcome == 1:
                    checking_node = par(checking_node)
                    reading_node = checking_node
                    ns = node_status(checking_node, 0)
                    continue
                elif O_func_outcome == 2:
                    #declare(checking_node)
                    print "Find HHH is {0} at time interval {1}".format(checking_node, time_interval)
                else:
                    print "Error: O_func_outcome can only be 1 or 2 after observation loop breaks"
            if checking_level < L_depth:
                O_func_outcome = 0
                while O_func_outcome == 0:
                    node_val = read(reading_node)
                    time_interval += 1
                    ns.x_mean = (ns.x_mean * ns.s + node_val) / float(ns.s+1.0)
                    ns.s += 1.0
                    O_func_outcome = O_func(ns.x_mean, ns.s, threshold, p_zero, p_zero)
                if O_func_outcome == 1:
                    checking_node = par(checking_node)
                    reading_node = checking_node
                    ns = node_status(checking_node, 0)
                    continue
                elif O_func_outcome == 2:
                    reading_node = left_child(checking_node)
                    O_func_outcome = 0
                    ns_reading = node_status(reading_node, 0)
                    while O_func_outcome == 0:
                        node_val = read(reading_node)
                        time_interval += 1
                        ns_reading.x_mean = (ns_reading.x_mean * ns_reading.s + node_val) / float(ns_reading.s+1.0)
                        ns_reading.s += 1.0
                        O_func_outcome = O_func(ns_reading.x_mean, ns_reading.s, threshold, p_zero, p_zero)
                    if O_func_outcome == 2:
                        checking_node = left_child(checking_node)
                        reading_node = checking_node
                        ns = ns_reading
                        continue
                    elif O_func_outcome == 1:
                        reading_node = right_child(checking_node)
                        O_func_outcome = 0
                        ns_reading = node_status(reading_node, 0)
                        while O_func_outcome == 0:
                            node_val = read(reading_node)
                            time_interval += 1
                            ns_reading.x_mean = (ns_reading.x_mean * ns_reading.s + node_val) / float(ns_reading.s+1.0)
                            ns_reading.s += 1.0
                            O_func_outcome = O_func(ns_reading.x_mean, ns_reading.s, threshold, p_zero, p_zero)
                        if O_func_outcome == 2:
                            checking_node = right_child(checking_node)
                            reading_node = checking_node
                            ns = ns_reading
                            continue
                        elif O_func_outcome == 1:
                            if p_zero < error:
                                #declare(checking_node)
                                print "Find HHH is {0} at time interval {1}".format(checking_node, time_interval)
                                break
                            else:
                                p_zero /= 2.0
                        else:
                            print "Error: O_func_outcome can only be 1 or 2 after observation loop breaks"
                    else:
                        print "Error: O_func_outcome can only be 1 or 2 after observation loop breaks"
        except EOFError:
            print "End of file error occurred."
            break
    # Close traffic file
    ff.close()
        
if __name__ == "__main__":
    rw_cb_algo()
