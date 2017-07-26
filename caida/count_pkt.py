"""
    Count aggregated packet count per destination ip.
"""

def count_pkt(infile, outfile):
    # key: dst_ip; value: No. of pkts received by dst_ip
    dst_pkts = {}
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n').split('\t')
            dst_ip = line[-1]
            # Ignore ipv6 pkts
            if dst_ip == "":
                continue
            # Aggregated under X.X.*.* prefix
            # Wildcard on the second two bytes
            two_bytes_prefix = ".".join(dst_ip.split('.')[:2])
            if not two_bytes_prefix in dst_pkts:
                dst_pkts[two_bytes_prefix] = 0
            dst_pkts[two_bytes_prefix] += 1

    with open(outfile, 'wb') as ff:
        for dst_ip in dst_pkts:
            count = dst_pkts[dst_ip]
            line = dst_ip + ',' + str(count) + '\n'
            ff.write(line)


def main():
    import glob, os

    indir = "test-data"
    infiles = glob.glob('{0}/*.anon.csv'.format(indir))
    infiles = sorted(infiles)
    print infiles
    for infile in infiles:
        filename = os.path.basename(infile)
        outfile = "{0}".format(filename.replace(".csv", ".agg.csv"))
        print outfile
        count_pkt(infile, outfile)
    
if __name__ == "__main__":
    main()

