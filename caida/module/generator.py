"""
    Use the traffic count from one file of caida trace (1mins time interval)
    as the lambdas to generate Poisson distribution.
"""
import numpy as np

def generator(leaf_lambdas):
    """
        :param leaf_lambdas: A list of leaf lambdas with (l,k) and lambda.
    """
    traffic = []
    for (l,k), leaf_lambda in leaf_lambdas:
        val = np.random.poisson(leaf_lambda)
        traffic.append([(l,k), val])
    return traffic        

def generator_file(leaf_lambdas, iterations, outfile):
    """ 
        :param leaf_lambdas: A list of leaf lambdas with (l,k) and lambda.
        :param outfile: Save a set of realization to outfile.
    """
    results = []
    for (l,k), val in leaf_lambdas:
        s = np.random.poisson(val, iterations)
        results.append(s)

    new_results = [[k[i] for k in results] for i in range(iterations)]
    with open(outfile, 'wb') as ff:
        for line in new_results:
            line = ','.join([str(k) for k in line]) + '\n'
            ff.write(line)
