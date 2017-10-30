# Generate traffic with poisson distribution
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

def generate_traffic():
    # Single HHH target
    lambda_lists = [20, 10, 1, 1, 1, 1, 1, 1]
    # Two HHHes 
    lambda_lists = [15, 15, 1, 1, 6, 8, 8, 8]
    traffic_file = "traffic_8nodes_poisson_multi.txt"

    results = []
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

if __name__ == "__main__":
    generate_traffic()
