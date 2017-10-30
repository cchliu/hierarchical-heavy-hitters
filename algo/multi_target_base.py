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
        #self.x_mean_net = x_mean

class Pointer(object):
    """Only handle one pointer."""

    def __init__(self, l, k, L, p0, eta, error, scale, logging_level, pid=None):
        self.p0, self.error =  p0, error
        self.alpha, self.beta = p0, p0
        self.depth, self.eta = L, eta
        self.leaf_alpha = error/float(3.0*L*get_constant(p0))*scale
        #self.leaf_alpha = error
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
        self.test = False
        self.time_interval = 0

        # Keep monitoring detected HHH nodes
        # key: (l,k), val: newNode object
        #self.HHH_nodes = {}
        
        # Logging module
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging_level)
        if pid:
            self.pid = pid
        else:
            self.pid = 0

    def _copyNode(self, node):
        # copyNode function wrapper
        # Overridden in subclass
        pass

    def _createNode(self, l, k):
        # createNode function wrapper
        # Overridden in subclass
        pass

    def isActive(self):
        return self.active

    def _report(self):
        # report function wrapper
        # Overridden in subclass
        pass

    def _debug_print(self, state, node, val, alpha, beta, output):
        # print debugging info
        # Overridden in subclass
        pass

    def _test_func(self, node, alpha, beta, eta):
        # test function wrapper
        # Overridden in subclass
        pass

    def _read(self, node, dvalues, HHH_nodes, alpha, beta):
        # read function wrapper
        # Overridden in subclass
        pass

    def run(self, dvalues, HHH_nodes):
        # Entry function
        self.time_interval += 1
        if self.curr_node.l == self.depth:
            if self.state == 0:
                return self.state_leaf(dvalues, HHH_nodes)
            else:
                self.logger.error("Pntr %d: Invalid state code %d at leaf level", self.pid, self.state)
        else:
            if self.state == 0:
                return self.state_s0(dvalues, HHH_nodes)
            elif self.state == 1:
                return self.state_s1(dvalues, HHH_nodes)
            elif self.state == 2:
                return self.state_s2(dvalues, HHH_nodes)
            else:
                self.logger.error("Pntr %d: Invalid state code %d at non-leaf level", self.pid, self.state)


    def state_s0(self, dvalues, HHH_nodes):
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
        self.logger.debug(reduce(lambda acc, k: acc+'{0}:{1}, {2} '.format(k, HHH_nodes[k].x_mean, HHH_nodes[k].x_mean_net), HHH_nodes, ''))
        # alpha, beta are different for the root node and non-root nodes.
        if self.curr_node.l == 0:
            alpha, beta = self.leaf_alpha, self.leaf_alpha
        else:
            alpha, beta = self.alpha, self.beta
        val = self._read(node, dvalues, HHH_nodes, alpha, beta)
        
        # alpha, beta are different for the root node and non-root nodes.
        if self.curr_node.l == 0:
            # If current pointer is at the root node.
            output = self._test_func(node, self.leaf_alpha, self.leaf_alpha, self.eta)
            self._debug_print('state_s0_root', node, val, self.leaf_alpha, self.leaf_alpha, output)

            if output == 0:
                # Stop the search and declare there is no more HHH.
                self.active = False
                return

        output = self._test_func(node, self.alpha, self.beta, self.eta)
        self._debug_print('state_s0', node, val, self.alpha, self.beta, output)

        if output == -1:
            # Continue taking samples
            return
        elif output == 0:
            # Move to the parent of node (l,k)
            parent_l, parent_k = get_parent(self.curr_node.l, self.curr_node.k)
            self.curr_node = self._createNode(parent_l, parent_k)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
        elif output == 1:
            self.state = 1
            left_child_l, left_child_k = get_left_child(self.curr_node.l, self.curr_node.k, self.depth)
            self.checking_node = self._createNode(left_child_l, left_child_k)
        else:
            self.logger.error("Pntr %d: Invalid test output = %d", self.pid, output)


    def state_s1(self, dvalues, HHH_nodes):
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
        val = self._read(node, dvalues, HHH_nodes, self.alpha, self.beta)

        output = self._test_func(node, self.alpha, self.beta, self.eta)
        self._debug_print('state_s1', node, val, self.alpha, self.beta, output)

        if output == -1:
            # Continue taking samples
            return
        elif output == 1:
            # Move the pointer to the left child of (l,k)
            left_child_l, left_child_k = get_left_child(self.curr_node.l, self.curr_node.k, self.depth)
            #self.curr_node = self._createNode(left_child_l, left_child_k, node)
            self.curr_node = self._copyNode(node)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
        elif output == 0:
            self.state = 2
            right_child_l, right_child_k = get_right_child(self.curr_node.l, self.curr_node.k, self.depth)
            self.checking_node = self._createNode(right_child_l, right_child_k)
        else:
            self.logger.error("Pntr %d: Invalid test output = %d", self.pid, output)
             

    def state_s2(self, dvalues, HHH_nodes):
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
        val = self._read(node, dvalues, HHH_nodes, self.alpha, self.beta)

        output = self._test_func(node, self.alpha, self.beta, self.eta)
        self._debug_print('state_s2', node, val, self.alpha, self.beta, output)

        if output == -1:
            # Continue taking samples
            return
        elif output == 1:
            # Move the pointer to the right child of (l,k)
            right_child_l, right_child_k = get_right_child(self.curr_node.l, self.curr_node.k, self.depth)
            #self.curr_node = self._createNode(right_child_l, right_child_k, node)
            self.curr_node = self._copyNode(node)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
        elif output == 0:
            if self.alpha < self.leaf_alpha:
                # Declare current node (l,k) as the target
                self._report()
                ret = self._copyNode(self.curr_node)
                # Reset pointer to the root node
                self.curr_node = self._createNode(0, 0)
                self.alpha, self.beta = self.p0, self.p0
                self.state = 0
                return ret
            else:
                self.alpha, self.beta = self.alpha/2.0, self.beta/2.0
                self.state = 0
                # Keep the old record or not?
                # Comparison shows that keeping record has better performance
                #self.curr_node = self._createNode(self.curr_node.l, self.curr_node.k)
        else:
            self.logger.error("Pntr %d: Invalid test output = %d", self.pid, output)


    def state_leaf(self, dvalues, HHH_nodes):
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
        val = self._read(node, dvalues, HHH_nodes, self.leaf_alpha, self.beta)

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
            self._report()
            ret = self._copyNode(self.curr_node)
            # Reset pointer to the root node
            self.curr_node = self._createNode(0, 0)
            self.alpha, self.beta = self.p0, self.p0
            self.state = 0
            return ret
        else:
            self.logger.error("Pntr %d: Invalid test output = %d", self.pid, output)
