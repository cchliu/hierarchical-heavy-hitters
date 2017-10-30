"""
    Pointer subclass: poisson distribution
"""
import math

from single_target_base import Pointer
from single_target_base import newNode

from tree_operations import read

def update_mean(node, val):
    node.x_mean = (node.x_mean * node.s + val) / float(node.s + 1.0)
    node.s = node.s + 1.0

class newNode_Poisson(newNode):
    def __init__(self, l, k, x_mean=None, s=None):
        super(newNode_Poisson, self).__init__(l, k)
        self.x_mean = x_mean if x_mean else 0
        self.s = s if s else 0

class Pointer_Poisson(Pointer):
    def __init__(self, l, k, L, p0, eta, error, scale, logging_level, xi):
        super(Pointer_Poisson, self).__init__(l, k, L, p0, eta, error, scale, logging_level)
        self.xi = xi

    def _createNode(self, l, k, *args, **kwargs):
        if len(args):
            node = args[0]
            return newNode_Poisson(l, k, node.x_mean, node.s)
        else:
            return newNode_Poisson(l, k)

    def _copyNode(self, node):
        return newNode_Poisson(node.l, node.k, node.x_mean, node.s)

    def _report(self):
        self.logger.info("Report node (l, k) = (%d, %d) as the target " +
            "at time interval %d, " +
            "p0 = %f, " +
            "eta = %f, " +
            "error = %f, " +
            "xi = %f, leaf_alpha = %.12f", self.curr_node.l, self.curr_node.k, \
            self.time_interval, self.p0, self.eta, self.error, self.xi, self.leaf_alpha)

    def _debug_print(self, state, node, val, alpha, beta, output):
        self.logger.debug("At time_interval = %d, " + 
            "%s: reading node (l, k) = (%d, %d), " + 
            "val = %f, x_mean = %f, s = %d, " + 
            "eta = %f, alpha = %.12f, beta = %.12f, test_output = %d", 
            self.time_interval, state, node.l, node.k, \
            val, node.x_mean, node.s, \
            self.eta, alpha, beta, output)

    def _read(self, node, dvalues, alpha, beta):
        val = read(node.l, node.k, dvalues)
        update_mean(node, val)
        return val

    def _test_func(self, node, alpha, beta, eta):
        x_mean, s = node.x_mean, node.s
        xi = self.xi
        a = math.sqrt(2.0*xi*math.log(2.0*s**3/float(alpha))/float(s))
        if x_mean - a > eta:
            return 1
        b = math.sqrt(2.0*xi*math.log(2.0*s**3/float(beta))/float(s))
        if x_mean + b < eta:
            return 0
        # Otherwise, continue taking samples
        return -1


