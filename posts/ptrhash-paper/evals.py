#!/usr/bin/env python3

import json
from math import log, floor, ceil
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def build_stats(f, out):
    alpha = 0.98

    with open(f) as f:
        all_data = json.load(f)

    cols = len(all_data)

    pcts = range(100)
    xs = [x / 100 for x in range(0, 101)]

    # Figure with 3 subplots
    fig, axs = plt.subplots(
        1, cols, figsize=(cols * 3 + 0.75, 2.5), layout="constrained"
    )
    if cols == 1:
        axs = [axs]
    keys = ["linear", "skewed", "optimal", "square", "cubic"]
    keys = [k for k in keys if k in all_data]

    for ax1, name in zip(axs, keys):
        data = all_data[name]["by_pct"]
        elem = 0
        elems = [0]
        for pct in pcts:
            elem += data[pct]["elements"]
            elems.append(elem)
        slots = elems[-1] / alpha
        load = [x / slots for x in elems]

        # Set plot size
        ax3 = ax1.twinx()
        ax2 = ax1.twinx()

        ax1.set_ylim(0, 1.0)
        ax3.set_ylim(0, 1)
        ax2.set_ylim(0, 10)

        ax1.set_title(name.capitalize())

        ax1.set_xlabel("Normalized bucket index")
        ax1.set_ylabel("Evictions per bucket")
        ax2.set_ylabel("Bucket size")
        ax2.yaxis.label.set_color("red")
        ax1.xaxis.set_minor_locator(MultipleLocator(0.1))

        p1 = ax1.plot(
            xs[1:],
            [data[pct]["evictions"] / data[pct]["buckets"] for pct in pcts],
            label="Evictions per bucket",
            color="black",
        )
        # Plot load factor
        p3 = ax3.fill(xs + [1], load + [0], color="red", alpha=0.1, label="Load factor")
        ax3.yaxis.set_visible(False)

        # Plot bucket size on secondary axis
        p2 = ax2.plot(
            xs[1:],
            [data[pct]["elements"] / data[pct]["buckets"] for pct in pcts],
            color="red",
            label="Bucket size",
        )

        ax1.set_zorder(ax3.get_zorder() + 1)
        ax1.set_frame_on(False)

        # Only show x and y ax
        ax1.spines["top"].set_visible(False)
        ax1.spines["bottom"].set_visible(False)
        ax1.spines["left"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax2.spines["bottom"].set_visible(False)
        ax2.spines["left"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax3.spines["top"].set_visible(False)
        ax3.spines["bottom"].set_visible(False)
        ax3.spines["left"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        # x and y from 0 to 1
        ax1.set_xlim(0, 1)
        # plt.ylim(0, 1)
        # plt.xlabel("Normalized hash")
        # plt.ylabel("Normalized bucket index")
        # Add horizontal grid lines
        ax1.grid(axis="y", lw=0.5)

        # Keep only leftmost and rightmost y-axis
        # First
        if name == keys[0]:
            ax1.yaxis.set_visible(True)
        else:
            ax1.set_yticklabels([])
            ax1.yaxis.set_ticks_position("none")
            ax1.set_ylabel(None)
        # Last
        if name == keys[-1]:
            ax2.yaxis.set_visible(True)
            if len(keys) > 1:
                ax1.legend(handles=p1 + p2 + p3, loc="best")
        else:
            ax2.yaxis.set_visible(False)

    plt.savefig(out, bbox_inches="tight")
    plt.close()


build_stats("data/build_stats_l35.json", "plots/build_stats_l35.svg")
build_stats("data/build_stats_l40.json", "plots/build_stats_l40.svg")
