import re
import sys

pattern = "At leaf_level = ([\d]+), error = ([\d.]+), at time = ([\d]+), stop the search. precision: ([\d.]+), recall: ([\d.]+)"

infile = sys.argv[1]
tt, precisions, recalls = [], [], []
with open(infile, 'rb') as ff:
    for line in ff:
        match = re.findall(pattern, line)
        if match:
            leaf_level, error, time_interval, p, r = match[0]
            p, r = float(p), float(r)
            time_interval = int(time_interval)
            tt.append(time_interval)
            precisions.append(p)
            recalls.append(r)
print "Monte carlo iterations: ", len(precisions)
print "Avg time interval: ", sum(tt)/float(len(tt))
print "Avg precision: ", sum(precisions)/float(len(precisions))
print "Avg recall: ", sum(recalls)/float(len(recalls))

            
