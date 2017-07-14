# Generate traffic with poisson distribution
"""
::Assume 8 leaf nodes
  prefix    lambda
  111       15
  110       15
  101       1
  100       1
  011       6
  010       8
  001       8
  000       8
"""
import numpy as np

lambda_lists = [15, 15, 1, 1, 6, 8, 8, 8]
traffic_file = "traffic_twoHHH.txt"

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


