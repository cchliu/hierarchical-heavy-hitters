import math
import numpy as np

def generate_traffic(lambda_lists, iters=None, traffic_file=None):
    if not traffic_file:
        traffic_file = "traffic_tmp.txt"

    results = []
    if not iters:
        iters = 1000
    for curr_l in lambda_lists:
        s = np.random.poisson(curr_l, iters)
        results.append(s)

    new_results = [[k[i] for k in results] for i in range(iters)]
    with open(traffic_file, 'wb') as ff:
        for line in new_results:
            line = ','.join([str(k) for k in line]) + '\n'
            ff.write(line)
    return traffic_file

def generate_ht(lambda_lists, sigma2, iters=None, traffic_file=None):
    if not traffic_file:
        traffic_file = "traffic_tmp.txt"
    # sigma**2 => 2
    results = []
    if not iters:
        iters = 1000
    for curr_l in lambda_lists:
        sigma = math.sqrt(sigma2)
        mu = math.log(curr_l)-(sigma**2)/2.0
        s = np.random.standard_normal(iters)
        s = [int(math.floor(math.exp(mu+sigma*k))) for k in s]
        results.append(s)

    new_results = [[k[i] for k in results] for i in range(iters)]
    with open(traffic_file, 'wb') as ff:
        for line in new_results:
            line = ','.join([str(k) for k in line]) + '\n'
            ff.write(line)
    return traffic_file
