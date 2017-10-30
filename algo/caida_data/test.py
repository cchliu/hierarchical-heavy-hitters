"""
    Create one set of lambdas for different K.
"""
def write2file(outfile, curr_vals):
    sorted_tags = sorted(curr_vals.keys(), key = lambda x:x[1])
    with open(outfile, 'wb') as ff:
        for node_tag in sorted_tags:
            l, k = node_tag
            line = "{0},{1},{2}".format(l, k, curr_vals[node_tag])
            ff.write(line + '\n')    

def main():
    curr_vals = {}
    leaf_level = 16
    infile = "equinix-chicago.dirA.20160406-140200.UTC.anon.agg.csv"
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n').split(',')
            prefix, val = line[0], int(line[1])
            b1, b2 = [int(k) for k in prefix.split('.')]
            index = b1 * 256 + b2 + 1
            tag = (leaf_level, index)
            curr_vals[tag] = val
    
    outfile = infile.replace('csv', 'l{0}.csv'.format(leaf_level))
    write2file(outfile, curr_vals)

    for leaf_level in range(15, 7, -1):
        next_vals = {}
        for node_tag in curr_vals:
            l, k = node_tag
            l -= 1
            k = (k+1)/2
            if not (l,k) in next_vals:
                next_vals[(l,k)] = 0
            next_vals[(l,k)] += curr_vals[node_tag]
        curr_vals = next_vals
        outfile = infile.replace('csv', 'l{0}.csv'.format(leaf_level))
        write2file(outfile, curr_vals)      

if __name__ == "__main__":
    main()
