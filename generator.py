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

lambda_lists = [20, 10, 1, 1, 1, 1, 1, 1]
traffic_file = "traffic.txt"

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


