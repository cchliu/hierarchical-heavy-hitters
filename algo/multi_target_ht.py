"""
    Pointer subclass: heavy-tailed distribution.
"""
import math

from multi_target_base import Pointer
from multi_target_base import newNode

from tree_operations import read_multi

def update_mean(node, val, alpha, beta, b, u, cS):
    # update x_mean_alpha
    threshold_alpha = (u*node.s/math.log(1.0/float(alpha)))**(1.0/float(b))
    node.x_mean_alpha = (node.x_mean_alpha * (node.s-1.0) + (val if val <= threshold_alpha*cS else 0))/float(node.s)
    #node.x_mean_alpha = (node.x_mean_alpha * node.s + val)/float(node.s+1.0)

    # update x_mean_beta
    threshold_beta = (u*node.s/math.log(1.0/float(beta)))**(1.0/float(b))
    node.x_mean_beta = (node.x_mean_beta * (node.s-1.0) + (val if val <= threshold_beta*cS else 0))/float(node.s)
    #node.x_mean_beta = (node.x_mean_beta * node.s + val)/float(node.s+1.0)

class newNode_HT(newNode):
    def __init__(self, l, k, x_mean=None, s=None):
        super(newNode_HT, self).__init__(l, k)
        self.x_mean = x_mean if x_mean else 0
        self.s = s if s else 0
        self.x_mean_net = self.x_mean
        self.x_mean_alpha = self.x_mean
        self.x_mean_beta = self.x_mean

class Pointer_HT(Pointer):
    def __init__(self, l, k, L, p0, eta, error, scale, logging_level, pid, b, u, cF, cS):
        super(Pointer_HT, self).__init__(l, k, L, p0, eta, error, scale, logging_level, pid)
        self.b, self.u = b, u
        self.cF, self.cS = cF, cS

    def _createNode(self, l, k):
        return newNode_HT(l, k)

    def _copyNode(self, node):
        ret = newNode_HT(node.l, node.k, node.x_mean, node.s)
        ret.x_mean_net = node.x_mean_net
        ret.x_mean_alpha = node.x_mean_alpha
        ret.x_mean_beta = node.x_mean_beta
        return ret

    def _report(self):
        self.logger.info("Pntr %d: Report node (l, k) = (%d, %d) as the target " +
            "at time interval %d, " +
            "net avg count = %f, " +
            "truncated sample mean alpha = %f, " +
            "truncated sample mean beta = %f, " + 
            "p0 = %f, " +
            "eta = %f, " +
            "error = %f, " +
            "b = %f, u = %f, leaf_alpha = %.12f", self.pid, self.curr_node.l, self.curr_node.k, \
            self.time_interval, self.curr_node.x_mean_net, \
            self.curr_node.x_mean_alpha, self.curr_node.x_mean_beta, \
            self.p0, self.eta, self.error, self.b, self.u, self.leaf_alpha)

    def _debug_print(self, state, node, val, alpha, beta, output):
	self.logger.debug("Pntr %d: At time_interval = %d, " +
            "%s: reading node (l, k) = (%d, %d), " +
            "val = %f, x_mean = %f, x_mean_net = %f, s = %d, " +
            "x_mean_alpha = %f, x_mean_beta = %f, " +
            "eta = %f, alpha = %.12f, beta = %.12f, test_output = %d",
            self.pid, self.time_interval, state, \
            node.l, node.k, val, node.x_mean, node.x_mean_net, node.s, \
            node.x_mean_alpha, node.x_mean_beta, \
            self.eta, alpha, beta, output)

    def _read(self, node, dvalues, HHH_nodes, alpha, beta):
        val = read_multi(node, dvalues, HHH_nodes)
        net_val = val - (node.x_mean - node.x_mean_net)
        update_mean(node, net_val, alpha, beta, self.b, self.u, self.cS)
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

