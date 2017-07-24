"""Assume there is only one HHH in the tree.

    There are two counters.
    In each time interval:
    - read aggregated count under monitored prefixes
    - report HHH based on measurement
    - determine which prefixes to monitor in the next interval
"""
from rwcb_multi_read import read_file, read_node
from rwcb_multi_statesman import par, left_child, right_child
def main():
    # Open traffic file
    infile = "traffic.txt"
    ff = open(infile, 'rb')

    # :param leaf_level: leaf level of the tree
    # :param threshold: HHH threshold
    leaf_level, root_level = 3, 0
    threshold = 25
    # Start from monitor the root node
    # Monitor the two children of root node
    p1, p2 = (1,1), (1,2)

    time_interval = 0
    while True:
        try:
            line = read_file(ff)
            time_interval += 1
            p1_val = read_node(p1, line, leaf_level)
            p2_val = read_node(p2, line, leaf_level)

            # Report HHH
            if p1_val >= threshold:
                print "At t={0}, node {1} is an HHH".format(time_interval, p1)
            if p2_val >= threshold:
                print "At t={0}, node {1} is an HHH".format(time_interval, p2)
            if p1_val < threshold and p2_val < threshold:
                if p1_val + p2_val >= threshold:
                    parent = par(p1, root_level) 
                    print "At t={0}, node {1} is an HHH".format(time_interval, parent)

            # Determine which prefixes to monitor in the next interval
            if p1_val >= threshold:
                if p1[0] < leaf_level:
                    p1, p2 = left_child(p1, leaf_level), right_child(p1, leaf_level)
                    continue
            elif p2_val >= threshold:
                if p2[0] < leaf_level:
                    p1, p2 = left_child(p2, leaf_level), right_child(p2, leaf_level)
                    continue
            elif p1_val + p2_val < threshold:
                parent = par(par(p1, root_level), root_level)
                p1, p2 = left_child(parent, leaf_level), right_child(parent, leaf_level)
                continue

        except EOFError:
            break


if __name__ == "__main__":
    main()
