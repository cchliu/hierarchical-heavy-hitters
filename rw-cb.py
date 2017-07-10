# Two pointers:
# Pointer p: current checking node
# Pointer q: current reading node

global time_interval
global threshold, epsno

# Stucture for current checking node
class node_status(object):
    def __init__(self, curr_s, p_zero):
        self.x_mean = 0
        self.s = curr_s
        self.p_zero = p_zero

global ns = node_status(0, p_zero)


def read(node, time_interval):
    ff.readline()
    return value

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

