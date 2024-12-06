#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
from math import log, floor, ceil
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


def bucket_fn_plots():

    def linear(x):
        return x

    def optimal(x):
        return x + (1 - x) * log(1 - x)

    def skew(x):
        beta = 0.6
        gamma = 0.3
        if x < beta:
            return x * gamma / beta
        else:
            return gamma + (x - beta) * (1 - gamma) / (1 - beta)

    def square(x):
        return x * x

    def cubic(x):
        return x * x * (1 + x) / 2

    def invert(f, y):
        l = 0
        h = 1
        for _ in range(20):
            m = (l + h) / 2
            if f(m) < y:
                l = m
            else:
                h = m
        return l

    lmbda = 4

    def bucket_sz(f, y):
        y1 = y
        y2 = y + 0.001
        x1 = invert(f, y1)
        x2 = invert(f, y2)
        return lmbda * (x2 - x1) * 1000

    xs = [x / 1000 for x in range(1000)]

    ## PLOT 1

    # Set plot size
    plt.figure(figsize=(4.5, 3))
    # Plot the functions from 0 to 1
    plt.plot(xs, [linear(x) for x in xs], label="Linear  $\\,x$")
    plt.plot(xs, [skew(x) for x in xs], label="Skewed $0.6\\mapsto0.3$")
    plt.plot(xs, [optimal(x) for x in xs], label="Optimal $x + (1{-}x)\\ln(1{-}x)$")
    plt.plot(xs, [square(x) for x in xs], label="Square $x^2$")
    plt.plot(xs, [cubic(x) for x in xs], label="Cubic   $(x^3+x^2)/2$")
    # plt.legend()
    # Only show x and y ax
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    # x and y from 0 to 1
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel("Normalized hash")
    plt.ylabel("Normalized bucket index")
    # Add horizontal grid lines
    plt.grid(axis="y", lw=0.5)

    plt.savefig("plots/bucket-fn.svg", bbox_inches="tight")
    plt.close()

    ## PLOT 2

    # Set plot size
    plt.figure(figsize=(4.5, 3))
    plt.plot(xs, [bucket_sz(linear, x) for x in xs], label="Linear   $\\,x$")
    plt.plot(xs, [bucket_sz(skew, x) for x in xs], label="Skewed $0.6\\mapsto0.3$")
    plt.plot(
        xs,
        [bucket_sz(optimal, x) for x in xs],
        label="Optimal $x + (1{-}x)\\ln(1{-}x)$",
    )
    plt.plot(xs, [bucket_sz(square, x) for x in xs], label="Square  $x^2$")
    plt.plot(xs, [bucket_sz(cubic, x) for x in xs], label="Cubic    $(x^3+x^2)/2$")
    plt.legend()
    # Only show x and y ax
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    # x and y from 0 to 1
    plt.xlim(0, 1)
    plt.ylim(0, 11.5)
    plt.xlabel("Normalized bucket index")
    plt.ylabel("Expected bucket size for $\\lambda = 4$")
    # Add horizontal grid lines
    plt.grid(axis="y", lw=0.5, which="major")
    plt.grid(axis="y", lw=0.5, which="minor", alpha=0.4)
    # Add minor tickes lines every 1
    plt.yticks(range(0, 12, 1), minor=True)

    plt.savefig("plots/bucket-size.svg", bbox_inches="tight")
    plt.close()


def build_stats(f, out, l):
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

        ax1.set_title(name.capitalize() + f" ($\\lambda = {l}$)")

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


def space(f, out):
    with open(f) as f:
        data = json.load(f)
    # Convert json to dataframe
    df = pd.DataFrame(data)
    print(df)

    df["c"] = 1000000000 * df["construction_6"] / df["n"]

    # A plot with lambda on the x-axis, and two y-axes with build time and size.
    # Create 6 lines, for 3 different alpha values and 2 different bucket functions.
    fig, ax = plt.subplots(1, 1, figsize=(7, 4), layout="constrained")
    ax2 = ax.twinx()

    ax.set_xlabel("$\\lambda$")
    ax.set_ylabel("Construction time (ns/key)")
    ax2.set_ylabel("Size (bits/key)")

    groups = df.groupby(["n", "alpha", "bucketfn"])
    for k, g in groups:
        n, alpha, bucketfn = k
        ls = "solid"
        lw = 1
        a = 1
        if n < 10**9:
            # ls = 'dashed'
            a = 0.3
        else:
            pass
        if bucketfn == "Linear":
            color = "blue"
        else:
            color = "red"
        if alpha == 0.99:
            lw = 1.2
        if alpha == 0.98:
            lw = 2.5
        ax.plot(g["lambda"], g["c"], label=f"{k}", ls=ls, color=color, lw=lw, alpha=a)
        if bucketfn == "CubicEps" and n == 10**9:
            ax2.plot(
                g["lambda"],
                g["total"],
                ls=ls,
                color="black",
                lw=lw,
                alpha=a,
            )

    ls = df["lambda"].unique()
    ys = [8 / l for l in ls]
    ax2.plot(ls, ys, lw=2.5, label="Space (pilots)", color="black", alpha=0.3)

    ax.set_xlim(2.95, 4.15)
    ax.set_ylim(0, 120)
    ax2.set_ylim(0, 3)
    ax2.grid(axis="y", lw=0.5)

    # Build legend
    llinear = mpatches.Patch(color="blue", label="Linear $\\gamma$ construction time")
    lcubic = mpatches.Patch(color="red", label="Cubic $\\gamma$ construction time")
    lspace = Line2D([0], [0], label="Total space", lw=2, color="black")
    lpilots = Line2D([0], [0], label="Pilots space", lw=2, color="black", alpha=0.3)
    la099 = Line2D([0], [0], label="$\\alpha = 0.99$", lw=1.5, color="black")
    la098 = Line2D([0], [0], label="$\\alpha = 0.98$", lw=2.25, color="black")
    plt.legend(
        handles=[llinear, lcubic, lpilots, lspace, la099, la098],
        loc="lower right",
        ncols=3,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.savefig(out, bbox_inches="tight")
    plt.show()
    plt.close()


# bucket_fn_plots()
# build_stats("data/bucket_fn_stats_l35.json", "plots/bucket_fn_stats_l35.svg", 3.5)
# build_stats("data/bucket_fn_stats_l40.json", "plots/bucket_fn_stats_l40.svg", 4.0)
space("data/size.json", "plots/size.svg")  #
