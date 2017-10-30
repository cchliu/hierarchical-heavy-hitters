"""
    Test if script test1 is correct.
"""
def main():
    base_file = "equinix-chicago.dirA.20160406-140200.UTC.anon.agg.csv"
    for leaf_level in range(16, 7, -1):
        total = 0
        infile = base_file.replace('csv', 'l{0}.csv'.format(leaf_level))
        with open(infile, 'rb') as ff:
            for line in ff:
                l, k, count = [int(i) for i in line.split(',')]
                total += count
        print total

if __name__ == "__main__":
    main()
