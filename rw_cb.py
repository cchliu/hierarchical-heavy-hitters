# Two pointers:
# Pointer p: current checking node
# Pointer q: current reading node

# :param time_interval: the index of current time interval
# :param file_handler: file object to read traffic data from
# :param levels: the depth of tree 
global time_interval, file_handler, levels
levels = 4

# threshold: HHH threshold
# epsno: parameter in equation (31) or (32)
global threshold, epsno, p_zero
p_zero = 1

# Stucture for current checking node
class node_status(object):
    def __init__(self, curr_s, p_zero):
        self.x_mean = 0
        self.s = curr_s
        self.p_zero = p_zero

global ns
ns = node_status(0, p_zero)


def read(node, time_interval):
    """Read traffic data of node at the current time_interval.

        :param node: The node whose value to read.
        :param time_interval: The current time interval.
    """
    global file_handler, levels
    ff = file_handler
    line = ff.readline().rstrip('\n')
    line = [int(k) for k in line.split(',')]
    node_val = 0
    for idx, val in enumerate(line):
        curr_level = levels-1
        curr_k = idx + 1
        while(curr_level >= 0):
            if node == (curr_level, curr_k):
                node_val += val
            curr_level -= 1
            curr_k = (curr_k + 1) / 2
    return node_val

def O_func(value):
    X_mean = (ns.x_mean * ns.s + value) / (ns.s + 1.0)
    curr_s = ns.s + 1.0
    # Calculate the equation
    equation_one = X_mean + sqrt(2*epsno*log(2*epsno*curr_s**3/p_zero)/curr_s)
    if equation_one < threshold:
        return 1
    equation_two = X_mean - sqrt(2*epsno*log(2*epsno*curr_s**3/p_zero)/curr_s)
    if equation_two > threshold:
        return 2
    # Neither equ(1) or equ(2) holds
    return 0

def rw_cb_algo():
    global file_handler
    infile = "traffic.txt"
    ff = open(infile, 'rb')
    file_handler = ff

    reading_node = (0, 1)
    print read(reading_node, 0)    
    """
    while True:
        read(reading_node)
        if O_func(reading_node) == 1:
            checking_node = par(checking_node)
            reading_node = checking_node
            continue
        elif O_func(reading_node) == 2:
            reading_node = left_child(checking_node)
            read(reading_node)
            if O_func(reading_node) == 2:
                checking_node = left_child(checking_node)
                reading_node = checking_node
                continue
            else:
                reading_node = right_child(checking_node)
                read(reading_node)
                if O_func(reading_node) == 2:
                    checking_node = right_child(checking_node)
                    reading_node = checking_node
                    continue
                else:
                    # Is it has to be O_func == 1?
                    if p_zero < errorness:
                        declare(checking_node)
                        break
                    else:
                        curr_s += 1
                        p_zero /= 2.0
        else:
            curr_s += 1
            continue
    """

if __name__ == "__main__":
    rw_cb_algo()
