"""
    Use the traffic count from one file of caida trace (1mins time interval)
    as the lambdas to generate Poisson distribution.

    *_ht: use the lambdas as mean to get sigma, scale factor for heavy-tailed 
    distribution.
"""
import math
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

def generator_ht(leaf_lambdas):
    """
        :param leaf_lambdas: A list of leaf_lambdas with (l,k) and lambda.
    """
    traffic = []
    for (l,k), leaf_lambda in leaf_lambdas:
        sigma = math.sqrt(math.log(leaf_lambda)*2.0)
        val = sigma * np.random.standard_normal(1)
        val = int(math.floor(math.exp(val)))
        traffic.append([(l,k), val])
    return traffic


def generator_chunk(leaf_lambdas, iterations):
    """
        :param leaf_lambdas: A list of leaf lambdas with (l,k) and lambda.
    """
    traffic = []
    for (l,k), leaf_lambda in leaf_lambdas:
        val = np.random.poisson(leaf_lambda, iterations)
        traffic.append(val)

    # Reshape traffic into a list of leaf_nodes:[ [(l,k), count]...]
    new_traffic = []
    for i in range(iterations):
        counts = [k[i] for k in traffic]
        leaf_nodes = [[pair[0], counts[idx]] for idx, pair in enumerate(leaf_lambdas)]
        new_traffic.append(leaf_nodes)
    return new_traffic

def generator_chunk_ht(leaf_lambdas, iterations):
    """
        :param leaf_lambdas: A list of leaf lambdas with (l,k) and lambda.
    """
    traffic = []
    for (l,k), leaf_lambda in leaf_lambdas:
        sigma = math.sqrt(math.log(leaf_lambda)*2.0)
        val = sigma * np.random.standard_normal(iterations)
        val = [int(math.floor(math.exp(k))) for k in val]
        traffic.append(val)

    # Reshape traffic into a list of leaf_nodes:[ [(l,k), count]...]
    new_traffic = []
    for i in range(iterations):
        counts = [k[i] for k in traffic]
        leaf_nodes = [[pair[0], counts[idx]] for idx, pair in enumerate(leaf_lambdas)]
        new_traffic.append(leaf_nodes)
    return new_traffic

    
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

def generator_file_ht(leaf_lambdas, iterations, outfile):
    """
        :param leaf_lambdas: A list of leaf lambdas with (l,k) and lambda.
        :param outfile: Save a set of realization to outfile.
    """
    results = []
    for (l,k), leaf_lambda in leaf_lambdas:
        sigma = math.sqrt(math.log(leaf_lambda)*2.0)
        val = sigma * np.random.standard_normal(iterations)
        val = [int(math.floor(math.exp(k))) for k in val]
        results.append(val)

    new_results = [[k[i] for k in results] for i in range(iterations)]
    with open(outfile, 'wb') as ff:
        for line in new_results:
            line = ','.join([str(k) for k in line]) + '\n'
            ff.write(line)

