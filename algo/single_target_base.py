"""
    ### Read a value at each time interval
    ### Change the state of the pointer.

    Encapsulate the pointer as an object.

    Pointer base class.
"""
import sys
import math
import logging
_EARLY_LOG_HANDLER = logging.StreamHandler(sys.stderr)
log = logging.getLogger()
if not len(log.handlers):
    log.addHandler(_EARLY_LOG_HANDLER)

from tree_operations import get_parent, get_left_child, get_right_child
from module.helper import get_constant
#****************************************#
class newNode(object):
    def __init__(self, l, k):
        self.l, self.k = l, k
        #self.x_mean, self.s = x_mean, s

class Pointer(object):
    def __init__(self, l, k, L, p0, eta, error, scale, logging_level):
        self.p0, self.error =  p0, error
        self.alpha, self.beta = p0, p0
        self.depth, self.eta = L, eta
        self.leaf_alpha = error/float(3.0*L*get_constant(p0))*scale
        self.state = 0
        
        # Debug
        # if s = 10
        # a = math.sqrt(2.0*xi*math.log(2.0*10**3/float(self.leaf_alpha))/float(10))
        # print "s = 10, a = %f" % a
        # if s = 1000
        # a = math.sqrt(2.0*xi*math.log(2.0*1000**3/float(self.leaf_alpha))/float(1000))
        # print "s = 1000, a = %f" % a

        self.curr_node = self._createNode(l, k)
        self.checking_node = self._createNode(l, k)
        self.active = True
        self.time_interval = 0
        # Logging module
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)

    def _createNode(self, l, k, *args, **kwargs):
        # createNode function wrapper
        # Overridden in subclass
        pass

    def _copyNode(self, node):
        # copyNode function wrapper
        # Overridden in subclass
        pass

    def isActive(self):
        return self.active

    def _report(self):
        # report function wrapper
        # Overridden in subclass
        pass

    def _debug_print(self, state, node, val, alpha, beta, output):
        # report function wrapper
        # Overridden in subclass
        pass

    def _test_func(self, node, alpha, beta, eta):
        # test function wrapper
        # Overridden in subclass
        pass

    def _read(self, node, dvalues, alpha, beta):
        # read function wrapper
        # Overridden in subclass
        pass

    def run(self, dvalues):
        # Entry function
        self.time_interval += 1
        if self.curr_node.l == self.depth:
            if self.state == 0:
                return self.state_leaf(dvalues)
            else:
                self.logger.error("Invalid state code %d at leaf level", self.state)
        else:
            if self.state == 0:
                return self.state_s0(dvalues)
            elif self.state == 1:
                return self.state_s1(dvalues)
            elif self.state == 2:
                return self.state_s2(dvalues)
            else:
                self.logger.error("Invalid state code %d at non-leaf level", self.state)


    def state_s0(self, dvalues):
        # Calcualte test output of node (l,k)
        # If test output = 0:
        #   Move to the parent of node (l,k)
        #   State = 0
        # Else if test output = 1:
        #   State = 1

        # Update x_mean and s
        # In state zero: the checking node is the current monitoring node.
        # Read aggregated value of the current checking node.
        node = self.curr_node
        val = self._read(node, dvalues, self.alpha, self.beta)

        output = self._test_func(node, self.alpha, self.beta, self.eta)
        self._debug_print('state_s0', node, val, self.alpha, self.beta, output)

        if output == -1:
            # Continue taking samples
            return
        elif output == 0:
            # Move to the parent of node (l,k)
            parent_l, parent_k = get_parent(self.curr_node.l, self.curr_node.k)
            #if (parent_l, parent_k) != (self.curr_node.l, self.curr_node.k):
            self.curr_node = self._createNode(parent_l, parent_k)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
        elif output == 1:
            self.state = 1
            left_child_l, left_child_k = get_left_child(self.curr_node.l, self.curr_node.k, self.depth)
            self.checking_node = self._createNode(left_child_l, left_child_k)
        else:
            self.logger.error("Invalid test output = %d", output)


    def state_s1(self, dvalues):
        # Calculate test output of left node of current pointer
        # If test output = 1:
        #   Move the pointer to the left child of (l,k)
        #   State = 0
        # Else if test output = 0:
        #   State = 2
        
        # Update x_mean and s
        # In state one: the checking node is the left node of current pointer
        # Read aggregated value of the current checking node
        node = self.checking_node
        val = self._read(node, dvalues, self.alpha, self.beta)

        output = self._test_func(node, self.alpha, self.beta, self.eta)
        self._debug_print('state_s1', node, val, self.alpha, self.beta, output)

        if output == -1:
            # Continue taking samples
            return
        elif output == 1:
            # Move the pointer to the left child of (l,k)
            left_child_l, left_child_k = get_left_child(self.curr_node.l, self.curr_node.k, self.depth)
            self.curr_node = self._createNode(left_child_l, left_child_k, node)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
        elif output == 0:
            self.state = 2
            right_child_l, right_child_k = get_right_child(self.curr_node.l, self.curr_node.k, self.depth)
            self.checking_node = self._createNode(right_child_l, right_child_k)
        else:
            self.logger.error("Invalid test output = %d", output)
             

    def state_s2(self, dvalues):
        # Calculate test output of right node of current pointer
        # If test output = 1:
        #   Move the pointer to the right child of (l,k)
        #   State = 0
        # Else if test output = 0:
        #   If alpha < threshold:
        #       Declare (l,k) as the target
        #   Else:
        #       Divide alpha and beta by 2

        # Update x_mean and s
        # In state two: the checking node is the right node of current pointer
        # Read aggregated value of the current checking node
        node = self.checking_node
        val = self._read(node, dvalues, self.alpha, self.beta)

        output = self._test_func(node, self.alpha, self.beta, self.eta)
        self._debug_print('state_s2', node, val, self.alpha, self.beta, output)

        if output == -1:
            # Continue taking samples
            return
        elif output == 1:
            # Move the pointer to the right child of (l,k)
            right_child_l, right_child_k = get_right_child(self.curr_node.l, self.curr_node.k, self.depth)
            self.curr_node = self._createNode(right_child_l, right_child_k, node)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
        elif output == 0:
            if self.alpha < self.leaf_alpha:
                # Declare current node (l,k) as the target
                self.active = False
                self._report()
                ret = self._copyNode(self.curr_node)
                return ret
            else:
                self.alpha, self.beta = self.alpha/2.0, self.beta/2.0
                self.state = 0
        else:
            self.logger.error("Invalid test output = %d", output)


    def state_leaf(self, dvalues):
        # Calculate test output of current node (l,k)
        # If test output = 0:
        #   Move the pointer to the parent of (l,k)
        #   State = 0
        # Else if test output = 1:
        #   Declare (l,k) as the target.

        # Update x_mean and s
        # In state leaf: the checking node is the current pointer
        # Read aggregated value of the current checking node.
        node = self.curr_node
        val = self._read(node, dvalues, self.leaf_alpha, self.beta)

        output = self._test_func(node, self.leaf_alpha, self.beta, self.eta)
        self._debug_print('state_leaf', node, val, self.leaf_alpha, self.beta, output)

        if output == -1:
            # Continue taking samples
            return
        elif output == 0:
            # Move to the parent of (l,k)
            parent_l, parent_k = get_parent(self.curr_node.l, self.curr_node.k)
            self.curr_node = self._createNode(parent_l, parent_k)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
        elif output == 1:
            # Declare (l,k) as the target
            self.active = False
            self._report()
            ret = self._copyNode(self.curr_node)
            return ret
        else:
            self.logger.error("Invalid test output = %d", output)
