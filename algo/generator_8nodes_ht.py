# Generate traffic with heavy-tailed distribution
"""
::Assume 8 leaf nodes
  prefix    lambda
  111       20
  110       10
  101       1
  100       1
  011       1
  010       1
  001       1
  000       1
"""
import numpy as np
import math

def generate_traffic():
    # Single HHH target
    #lambda_lists = [20, 10, 1, 1, 1, 1, 1, 1]
    #traffic_file = "traffic_8nodes_ht.txt"
    # Two HHHes 
    lambda_lists = [15, 15, 1, 1, 6, 8, 8, 8]
    traffic_file = "traffic_8nodes_ht_multi.txt"
    
    sigma2 = 0.70
    # Calculate for parameter u
    u = 0
    for curr_l in lambda_lists:
        sigma = math.sqrt(sigma2)
        mu = math.log(curr_l)-(sigma**2)/2.0
        tmp = math.exp(2.0*mu + 2.0*sigma**2)
        if u < tmp:
            u = tmp
    print u
    # sigma**2 => 2
    results = []
    iters = 5000
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

if __name__ == "__main__":
    generate_traffic()
