"""
### Read values of current time interval.
### Update the rules online.

"""
import logging

from module.metric import precision, recall
from tree_operations import construct
from minlan_algo import MinlanAlgo


def main():
    infile = 'traffic_8nodes_poisson_multi.txt'
    eta = 25
    L = 3

    # Sorted leaf tags
    sorted_leaf_tags = [(L, idx) for idx in range(8)]

    monitor = MinlanAlgo(L, eta, 2, logging.DEBUG)
    time_interval = 0
    with open(infile, 'rb') as ff:
        for line in ff:
            time_interval += 1
            values = [int(k) for k in line.split(',')]
            dvalues = construct(values, sorted_leaf_tags)
            monitor.run(dvalues)

if __name__ == "__main__":
    main()

