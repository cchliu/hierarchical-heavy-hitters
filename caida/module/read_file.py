"""Read leaf node counts from file."""
def read_file(file_handler, leaf_lambdas):
    """
        :returns: A list of leaf nodes with (l,k) and count.
    """
    ff = file_handler
    line = ff.readline().rstrip("\n")
    if not line:
        raise EOFError
    counts = [int(k) for k in line.split(',')]
    leaf_nodes = [[pair[0], counts[idx]] for idx, pair in enumerate(leaf_lambdas)]
    return leaf_nodes

def read_file_old(file_handler, leaf_level):
    """
        :returns: A list of leaf nodes with (l,k) and count.
    """
    ff = file_handler
    line = ff.readline().rstrip("\n")
    if not line:
        raise EOFError
    counts = [int(k) for k in line.split(',')]
    leaf_nodes = [[(leaf_level, idx+1), val] for idx, val in enumerate(counts)]
    return leaf_nodes
