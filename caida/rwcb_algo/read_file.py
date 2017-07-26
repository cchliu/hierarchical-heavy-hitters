"""Read leaf node counts from file."""
def read_file(file_handler, leaf_level):
    """
        :returns: A list of leaf nodes with (l,k) and count.
    """
    ff = file_handler
    line = ff.readline().rstrip("\n")
    if not line:
        raise EOFError
    counts = [int(k) for k in line.split(',')]
    leaf_nodes = [[(leaf_level, idx+1), count] for idx, count in enumerate(counts)]
    return leaf_nodes

