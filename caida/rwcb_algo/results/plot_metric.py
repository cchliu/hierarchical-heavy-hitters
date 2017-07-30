""" 
    Plot precision/recall over time intervals.
"""
import matplotlib.pyplot as plt
import re

infile = "perf_v2.txt"
precisions, recalls = [], []

pattern = r"precision: ([\d.]+), recall: ([\d.]+)"
with open(infile, 'rb') as ff:
    for line in ff:
        match = re.findall(pattern, line)
        if match:
            p, r = [float(k) for k in match[0]]
            precisions.append(p)
            recalls.append(r)
data_size = len(precisions)

time_intervals = [i+1 for i in range(data_size)]
fig = plt.figure()
axes = fig.add_subplot(1,1,1)
plt.plot(time_intervals, precisions)
axes.set_xlabel('time_intervals')
axes.set_ylabel('Precision')
plt.savefig("precision.png")

fig = plt.figure()
axes = fig.add_subplot(1,1,1)
plt.plot(time_intervals, recalls)
axes.set_xlabel('time_intervals')
axes.set_ylabel('Recall')
plt.savefig("recall.png")


