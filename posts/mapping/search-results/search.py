#!/usr/bin/env python3
import pandas as pd
import tabulate
import matplotlib.pyplot as plt
from matplotlib import ticker

# plt.style.use("ggplot")
# plt.rcParams["axes.facecolor"] = "#fbfbfb"

# cols:
# - pattern len
# - text len
# - dist
# - trace
# - k
# - t search
# - t edlib
df = pd.read_json("search.json")

df["search"] = df["search"] / df["text_len"]
df["edlib"] = df["edlib"] / df["text_len"]
df["speedup"] = df["edlib"] / df["search"]
df["dist"] = (df["dist"] * 100).astype(int)

df = df[df.trace == False]

# p = df.pivot_table(
#     index=["pattern_len", "dist"],
#     columns=[],
#     values=["edlib", "search", "speedup"],
# )
# # p = p.swaplevel(0, 1, axis=1).sort_index(axis=1)
# p = p.reset_index()
# print(
#     tabulate.tabulate(
#         p, headers=p.columns, tablefmt="orgtbl", floatfmt=".1f", showindex=False
#     )
# )


f = pd.melt(df, id_vars=["pattern_len", "dist", "k"], value_vars=["edlib", "search"])

# print(f)

# line plot
ax = plt.gca()
for key, g in f.groupby(["variable", "dist", "k"]):
    (variable, dist, k) = key
    if variable == "search":
        if dist != 100:
            continue
        if k != -1:
            continue
        c = "#ffc107"
        l = "SIMD search"
        lw = 2
    else:
        l = f"Edlib ({dist}%)"
        if dist == 100:
            c = "#000000"
            lw = 1.5
        elif dist == 10:
            c = "#999999"
            lw = 2
        else:
            c = "#cccccc"
            lw = 3
    ls = "-"
    if k != -1:
        ls = "dashed"
        lw -= 0.5
        if dist == 100:
            plt.plot([], [], color=c, label="Edlib: doubling", lw=1)
            l = "Edlib: full matrix"
        else:
            l = ""
    g.plot(x="pattern_len", y="value", color=c, label=l, ax=ax, lw=lw, ls=ls)

plt.xlabel("Pattern length")
plt.ylabel("Time per text character (ns)")
plt.yscale("log", base=2)
plt.xscale("log", base=2)
plt.yticks([8, 11, 16, 30, 50, 100, 200])
ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
plt.grid(True, which="major", axis="y", lw=0.5, color="grey", ls="dotted")
# Hide right of plot frame
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)

plt.legend()
(hs, ls) = ax.get_legend_handles_labels()
hs = [hs[3], hs[4], hs[2], hs[1], hs[0], hs[5]]
ls = [ls[3], ls[4], ls[2], ls[1], ls[0], ls[5]]
plt.legend(hs, ls, title="Method (divergence)")
plt.tight_layout()
# Set size
fig = plt.gcf()
fig.set_size_inches(6, 4)
plt.savefig("search-plot.svg", bbox_inches="tight")
# plt.show()
plt.close()
