import math

def load_lambdas(infile):
    """
        :param infile: Read one instance of caida trace. Use the value as the leaf lambdas.
        
        :returns: leaf lambdas, a list of [(l,k),lambda].
    """
    leaf_lambdas = []
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n').split(',')
            l, k, count = [int(i) for i in line]
            leaf_lambdas.append([(l,k), count])

    # Sort leaf_lambdas
    leaf_lambdas = sorted(leaf_lambdas, key = lambda x:x[0][1])

    # Scale leaf lambdas, < 1000
    max_lambda = max([k[1] for k in leaf_lambdas])
    x1 = int(math.log(max_lambda, 10))
    if x1 + 1 > 3:
        x2 = x1 + 1 - 3
        for i in range(len(leaf_lambdas)):
            leaf_lambdas[i][1] = int(leaf_lambdas[i][1] / float(10**(x2)))

    return leaf_lambdas


