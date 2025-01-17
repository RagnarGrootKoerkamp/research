#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
from math import log, floor, ceil
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import tabulate


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
    plt.show()
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
    plt.show()
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
    plt.show()
    plt.close()


def space(f, out):
    with open(f) as f:
        data = json.load(f)
    # Convert json to dataframe
    df = pd.DataFrame(data)

    df["c"] = 1000000000 * df["construction_6"] / df["n"]

    # A plot with lambda on the x-axis, and two y-axes with build time and size.
    # Create 6 lines, for 3 different alpha values and 2 different bucket functions.
    fig, ax = plt.subplots(1, 1, figsize=(9, 5), layout="constrained")
    ax2 = ax.twinx()

    ax.set_xlabel("$\\lambda$")
    ax.set_ylabel("Construction time (ns/key)")
    ax2.set_ylabel("Size (bits/key)")

    # TODO DROP
    df = df[df["alpha"] != 0.999]
    df = df[df["alpha"] != 0.997]

    alpha_size = {
        0.998: 0.8,
        0.995: 1.2,
        0.99: 1.6,
        0.98: 2.0,
    }

    groups = df.groupby(["n", "alpha", "bucketfn", "real_alpha"])
    for k, g in groups:
        print(k)
        n, alpha, bucketfn, real_alpha = k
        ls = "solid"
        lw = alpha_size[alpha]
        a = 0.8
        if bucketfn == "Linear":
            color = "blue"
        else:
            color = "red"
        ax.plot(g["lambda"], g["c"], label=f"{k}", ls=ls, color=color, lw=lw, alpha=a)

    ls = df["lambda"].unique()
    ys = [8 / l for l in ls]
    ax2.plot(ls, ys, lw=1, label="Space (pilots)", color="black")
    # Plot space with remap
    for alpha in df.alpha.unique():
        lw = alpha_size[alpha]
        ax2.plot(
            ls,
            [8 / l + 32 * (1 / alpha - 1) for l in ls],
            lw=lw,
            color="green",
            alpha=0.9,
        )
        if alpha < 0.995:
            ax2.plot(
                ls,
                [8 / l + (512 / 44) * (1 / alpha - 1) for l in ls],
                lw=lw,
                color="orange",
                alpha=0.9,
            )

    # Add dots for the simple configuration
    l = 3.0
    a = 0.995
    y = df[(df.alpha == a) & (df.bucketfn == "Linear") & (df["lambda"] == l)].c
    ax.plot(l, y, "bo", ms=9)
    y = 8 / l + 32 * (1 / a - 1)
    ax2.plot(l, y, "o", color="green", ms=8, mew=2, mec="blue")

    # Add dots for the compact configuration
    l = 4.0
    a = 0.99
    y = df[(df.alpha == a) & (df.bucketfn == "CubicEps") & (df["lambda"] == l)].c
    ax.plot(l, y, "ro", ms=9)
    y = 8 / l + (512 / 44) * (1 / a - 1)
    # Red outline to marker
    ax2.plot(l, y, "o", color="orange", ms=8, mew=2, mec="red")

    ax.set_xlim(2.66, 4.24)
    ax.set_ylim(0, 140)
    ax2.set_ylim(0, 3.5)
    ax2.grid(axis="y", lw=0.5)
    ax.grid(axis="x", lw=0.5)
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    ax2.set_yticks([2.1, 2.2, 2.3, 2.4, 2.6, 2.7, 2.8, 2.9], minor=True)
    ax2.grid(axis="y", lw=0.5, which="minor", alpha=0.4)

    # Build legend
    llinear = mpatches.Patch(color="blue", label="Linear $\\gamma$")
    lcubic = mpatches.Patch(color="red", label="Cubic $\\gamma$")
    lpilots = Line2D([0], [0], label="Pilots space", lw=2, color="black")
    lfill = Line2D([], [], label="", lw=0)
    lvec = Line2D([0], [0], label="Total space, Vec<u32>", lw=2, color="green")
    lclef = Line2D([0], [0], label="Total space, CLEF", lw=2, color="orange")
    la = []
    for a in sorted(df.alpha.unique(), reverse=True):
        lw = alpha_size[a]
        l = Line2D([0], [0], label=f"$\\alpha = {a}$", lw=lw, color="black")
        la.append(l)
    plt.legend(
        handles=[llinear, lcubic, lfill, lpilots, lvec, lclef] + la,
        loc="lower right",
        ncols=5,
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


def remap(f):
    with open(f) as f:
        data = json.load(f)
    # Convert json to dataframe
    df = pd.DataFrame(data)
    # Print dataframe with two digits precision.
    df = df[
        [
            "alpha",
            "lambda",
            "bucketfn",
            "pilots",
            "q1_phf",
            "q32_phf",
            "remap_type",
            "remap",
            "q1_mphf",
            "q32_mphf",
        ]
    ]

    print(tabulate.tabulate(df, headers=df.columns, tablefmt="orgtbl", floatfmt=".3f"))

    # Two side by side plots
    # fig, axs = plt.subplots(1, 2, figsize=(7, 4), layout="constrained")
    # groups = df.groupby(["bucketfn"])
    # for ax, (k, g) in zip(axs, groups):
    #     # Bar plot, x = remap_typ
    #     # y = total, q_mphf

    #     ax.plot(g["remap_type"], g["q_phf"], label="Q-PHF", color="red")
    #     ax.plot(g["remap_type"], g["q_mphf"], label="Q-MPHF", color="blue")
    #     ax.set_ylim(0, 25)

    #     ax2 = ax.twinx()
    #     ax2.plot(g["remap_type"], g["total"], label="Total", color="black")
    #     ax2.plot(g["remap_type"], g["pilots"], label="Pilots", color="black")

    #     ax2.set_ylim(0, 3.5)

    # plt.show()
    # plt.close()


def query_batching(f, out):
    with open(f) as f:
        data = json.load(f)
    # Convert json to dataframe
    df = pd.DataFrame(data)

    # A plot with lambda on the x-axis, and two y-axes with build time and size.
    # Create 6 lines, for 3 different alpha values and 2 different bucket functions.
    fig, axs = plt.subplots(1, 2, figsize=(7, 3), layout="constrained")

    for ax in axs:
        ax.set_xlabel("Batch or lookahead size")
    axs[0].set_ylabel("Query throughput (ns/key)")

    groups = df.groupby(["n", "alpha", "bucketfn", "mode"])
    for k, g in groups:
        n, alpha, bucketfn, mode = k
        ls = "solid"
        lw = 1
        a = 0.8
        ax = axs[1]
        if n < 10**9:
            # a = 0.5
            # lw += 1
            ax = axs[0]
        if bucketfn == "Linear":
            color = "blue"
        else:
            color = "red"
        if mode == "stream":
            ls = "dashed"
        if mode == "batch":
            ls = "dashdot"
            continue
        if mode == "batch2":
            # ls = "dashdot"
            ls = "dotted"
        ax.plot(g["batch_size"], g["q_phf"], ls=ls, color=color, lw=lw, alpha=a)

        if mode == "loop":
            # Horizontal line at height g['q_phf']
            assert len(g) == 1
            ax.axhline(y=g["q_phf"].values[0], color=color, lw=lw, ls=ls)

    for ax in axs:
        ax.set_xscale("log")
        ax.set_xticks([2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128])
        ax.set_xticks([1, 3, 5, 7, 10, 14, 20, 28, 40, 56, 80, 112], minor=True)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: int(x)))
        ax.xaxis.set_minor_formatter(plt.FuncFormatter(lambda x, _: None))
        ax.set_xlim(1, 64)
        ax.grid(axis="y", lw=0.5)
        ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    axs[0].set_ylim(0, 20)
    axs[1].set_ylim(0, 20)

    for ax in axs:
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Build legend
    lcompact = mpatches.Patch(color="red", label="Compact")
    lsimple = mpatches.Patch(color="blue", label="Simple")
    lloop = Line2D([0], [0], label="Looping", lw=2, color="black", ls="solid")
    lbatch = Line2D([0], [0], label="Batching", lw=2, color="black", ls="dotted")
    lstream = Line2D([0], [0], label="Streaming", lw=2, color="black", ls="dashed")
    lfill = Line2D([], [], label="", lw=0)
    axs[0].legend(
        handles=[lcompact, lsimple, lfill, lloop, lbatch, lstream],
        loc="upper left",
        ncols=2,
    )

    plt.savefig(out, bbox_inches="tight")
    plt.show()
    plt.close()


class MulticolorPatch(object):
    def __init__(self, label, styles):
        self.styles = styles
        self.label = label

    def get_label(self):
        return self.label


# define a handler for the MulticolorPatch object
class MulticolorPatchHandler(object):
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        width, height = handlebox.width, handlebox.height
        patches = []
        for i, style in enumerate(orig_handle.styles):
            patches.append(
                plt.Rectangle(
                    [
                        width / len(orig_handle.styles) * i - handlebox.xdescent,
                        -handlebox.ydescent,
                    ],
                    width / len(orig_handle.styles),
                    height,
                    edgecolor="none",
                    linewidth=0,
                    **style,
                )
            )

        patch = PatchCollection(patches, match_original=True)

        handlebox.add_artist(patch)
        return patch


def query_throughput(f, out):
    with open(f) as f:
        data = json.load(f)
    # Convert json to dataframe
    df = pd.DataFrame(data)

    # A plot with lambda on the x-axis, and two y-axes with build time and size.
    # Create 6 lines, for 3 different alpha values and 2 different bucket functions.
    fig, axs = plt.subplots(1, 1, figsize=(4, 3), layout="constrained")
    axs = [axs]

    print("Fastest: ", df["q_phf"].min())

    print(df[(df["alpha"] == 0.995) & (df["threads"] == 1) & (df["n"] == 10**9)])

    aa = 0.4

    for ax in axs:
        ax.set_xlabel("#threads")
    axs[0].set_ylabel("Query throughput (ns/key)")

    groups = df.groupby(["n", "alpha", "bucketfn", "mode", "remap_type"])
    for k, g in groups:
        print(k)
        print(g)
        n, alpha, bucketfn, mode, remap_type = k
        ls = "solid"
        lw = 2
        ax = axs[0]

        if bucketfn == "CubicEps" and remap_type != "CacheLineEF":
            continue

        if n < 10**9:
            continue
            ax = axs[0]
        if bucketfn == "Linear":
            c1 = "blue"
            c2 = "green"
        else:
            c1 = "red"
            c2 = "orange"
        if mode == "stream":
            ls = "dashed"
        if mode == "batch":
            ls = "dotted"
        ax.plot(g["threads"], g["q_phf"], ls=ls, color=c1, lw=1.5, alpha=1.0)
        ax.plot(g["threads"], g["q_mphf"], ls=ls, color=c1, lw=2, alpha=aa)

    # Perfect scaling plot.
    xs = [1, 2, 3, 4, 5, 6, 7]
    ax.plot(
        xs,
        [df[(df["n"] == 10**9) & (df["threads"] == 1)]["q_phf"].min() / x for x in xs],
        color="black",
        lw=0.5,
    )

    for ax in axs:
        ax.grid(axis="y", lw=aa)
        ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    axs[0].set_ylim(0, 21.5)
    axs[0].set_xlim(0.8, 6.2)

    axs[0].axhline(y=2.5, color="black", lw=1, ls="dotted", zorder=-1)

    for ax in axs:
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Build legend
    lcompact = MulticolorPatch(
        "Compact", [{"color": "red", "alpha": 1.0}, {"color": "red", "alpha": aa}]
    )
    lsimple = MulticolorPatch(
        "Simple", [{"color": "blue", "alpha": 1.0}, {"color": "blue", "alpha": aa}]
    )
    lphf = MulticolorPatch(
        "PHF", [{"color": "red", "alpha": 1.0}, {"color": "blue", "alpha": 1.0}]
    )
    lmphf = MulticolorPatch(
        "MPHF", [{"color": "red", "alpha": aa}, {"color": "blue", "alpha": aa}]
    )
    lloop = Line2D([0], [0], label="Looping", lw=1.5, color="black", ls="solid")
    lstream = Line2D([0], [0], label="Streaming", lw=2, color="black", ls="dashed")
    lopt = Line2D([0], [0], label="RAM throughput", lw=1, color="black", ls="dotted")
    lscaling = Line2D(
        [0], [0], label="Perfect scaling", lw=0.5, color="black", ls="solid"
    )
    axs[0].legend(
        handles=[lcompact, lsimple, lphf, lmphf, lloop, lstream, lopt, lscaling],
        loc="upper right",
        ncols=2,
        handler_map={MulticolorPatch: MulticolorPatchHandler()},
    )

    plt.savefig(out, bbox_inches="tight")
    plt.show()
    plt.close()


# bucket_fn_plots()
# build_stats("data/bucket_fn_stats_l35.json", "plots/bucket_fn_stats_l35.svg", 3.5)
# build_stats("data/bucket_fn_stats_l40.json", "plots/bucket_fn_stats_l40.svg", 4.0)
# space("data/size.json", "plots/size.svg")
remap("data/remap.json")
# NOTE: compact looping is slow because of SIMD.
# query_batching("data/query_batching.json", "plots/query_batching.svg")
# query_throughput("data/query_throughput.json", "plots/query_throughput.svg")

# TODO: sharding
