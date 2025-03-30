#!/usr/bin/env python

# Plot the values of v.
import matplotlib.pyplot as plt
from pathlib import Path

plen = 100

lines = Path("vecs").read_text().splitlines()
lines.reverse()
alphas = [1.0, 0.5, 0.0]
comment = ["semi-global", "skip-cost", "overlap"]
for i in range(len(lines) - 1, -1, -1):
    v = eval(lines[i])
    l = len(v)
    plt.plot(v, label=f"skip-cost={alphas[i]:.1f}, {comment[i]}")
plt.ylim(0, 100)
plt.xlim(0, l)
plt.axvline(x=plen, color="black", linewidth=0.5)
plt.axvline(x=len(v) - plen, color="black", linewidth=0.5)
plt.legend(ncols=1)

# Reverse the legend order
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles[::-1], labels[::-1])

plt.xlabel("Position")
plt.ylabel("Cost")
# Set size
fig = plt.gcf()
fig.set_size_inches(10, 3)
plt.savefig("skip-cost-plot.svg", bbox_inches="tight")
plt.close()
