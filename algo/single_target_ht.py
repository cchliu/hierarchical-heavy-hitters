"""
    Pointer subclass: heavy-tailed distribution.
"""
import math

from single_target_base import Pointer
from single_target_base import newNode

from tree_operations import read

def update_mean(node, val, alpha, beta, b, u):
    # update x_mean_alpha
    threshold_alpha = (u*(node.s+1)/math.log(1.0/float(alpha)))**(1.0/float(b))
    node.x_mean_alpha = (node.x_mean_alpha * node.s + (val if val <= threshold_alpha else 0))/float(node.s+1.0)
    #node.x_mean_alpha = (node.x_mean_alpha * node.s + val)/float(node.s+1.0)
    # update x_mean_beta
    threshold_beta = (u*(node.s+1)/math.log(1.0/float(beta)))**(1.0/float(b))
    node.x_mean_beta = (node.x_mean_beta * node.s + (val if val <= threshold_beta else 0))/float(node.s+1.0)
    #node.x_mean_beta = (node.x_mean_beta * node.s + val)/float(node.s+1.0)
    # update s
    node.s = node.s + 1.0

class newNode_HT(newNode):
    def __init__(self, l, k, x_mean=None, s=None):
        super(newNode_HT, self).__init__(l, k)
        self.x_mean_alpha = x_mean[0] if x_mean else 0
        self.x_mean_beta = x_mean[1] if x_mean else 0
        self.s = s if s else 0

class Pointer_HT(Pointer):
    def __init__(self, l, k, L, p0, eta, error, scale, logging_level, b, u, cF):
        super(Pointer_HT, self).__init__(l, k, L, p0, eta, error, scale, logging_level)
        self.b, self.u = b, u
        self.cF = cF

    def _createNode(self, l, k, *args, **kwargs):
        if len(args):
            node = args[0]
            return newNode_HT(l, k, (node.x_mean_alpha, node.x_mean_beta), node.s)
        else:
            return newNode_HT(l, k)

    def _copyNode(self, node):
        ret = newNode_HT(node.l, node.k, (node.x_mean_alpha, node.x_mean_beta), node.s)
        return ret

    def _report(self):
        self.logger.info("Report node (l, k) = (%d, %d) as the target " +
            "at time interval %d, " +
            "p0 = %f, " +
            "eta = %f, " +
            "error = %f, " +
            "b = %f, u = %f, leaf_alpha = %.12f", self.curr_node.l, self.curr_node.k, \
            self.time_interval, self.p0, self.eta, self.error, self.b, self.u, self.leaf_alpha)

    def _debug_print(self, state, node, val, alpha, beta, output):
        self.logger.debug("At time_interval = %d, " +
            "%s: reading node (l, k) = (%d, %d), " +       
            "val = %f, x_mean_alpha = %f, x_mean_beta = %f, s = %d, " +  
            "eta = %f, alpha = %.12f, beta = %.12f, test_output = %d",
            self.time_interval, state, node.l, node.k, \
            val, node.x_mean_alpha, node.x_mean_beta, node.s, \
            self.eta, alpha, beta, output)

    def _read(self, node, dvalues, alpha, beta):
        val = read(node.l, node.k, dvalues)
        update_mean(node, val, alpha, beta, self.b, self.u)
        return val

    def _test_func(self, node, alpha, beta, eta):
	x_mean_alpha, x_mean_beta = node.x_mean_alpha, node.x_mean_beta
        s = node.s
        b, u = self.b, self.u
        a = 4*u**(1/float(b))*(math.log(2.0*s**3/float(alpha))/float(s))**((b-1)/float(b))
        a = a * self.cF
        if x_mean_alpha - a > eta:
            return 1
        b = 4*u**(1/float(b))*(math.log(2.0*s**3/float(beta))/float(s))**((b-1)/float(b))
        b = b * self.cF
        if x_mean_beta + b < eta:
            return 0
        # Otherwise, continue taking samples
        return -1
