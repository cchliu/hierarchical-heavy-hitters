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
    
    
