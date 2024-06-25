import os
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from math import log
import matplotlib as mpl

# Deterministic svg output.
os.environ["SOURCE_DATE_EPOCH"] = "0"
mpl.rcParams["svg.hashsalt"] = "0"
# High quality png output.
mpl.rcParams["figure.dpi"] = 400


def read():
    with open(f"data.json", "r") as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    df = df.rename(columns={"tp.minimizer_type": "Minimizer type"})
    # In type column replace minizer value with random minimizer.
    df["Minimizer type"] = df["Minimizer type"].replace("Minimizer", "Random minimizer")
    df["Minimizer type"] = df["Minimizer type"].replace("ModMinimizer", "Mod-minimizer")
    return df


def plot(df, name, bounds=False):
    ks = range(df.k.min(), df.k.max() + 1)
    ymin = 0.95 * 1 / df.w.max()
    ymax = 1.05 * 2 / (df.w.min() + 1)
    w = df.w.unique()[0]

    (fig, ax) = plt.subplots()

    ax.axhline(y=1 / (w), color="black", linewidth=0.5)
    ax.axhline(y=2 / (w + 1), color="black", linewidth=0.5)
    ax.plot(ks, [1.5 / (w + k - 0.5) for k in ks], color="green", linewidth=0.5)
    if bounds:
        ax.plot(
            ks,
            [(k + 2 * w - 1) // (w) / (k + w) for k in ks],
            color="blue",
            linewidth=0.5,
        )
        ax.plot(
            ks,
            [(k + 2 * w - 1) / (w) / (k + w) for k in ks],
            color="purple",
            linewidth=0.5,
        )

    offset = 0.05
    ax.text(
        1.05,
        offset,
        f"1.5/(w+k-0.5) previous bound",
        color="green",
        transform=plt.gca().transAxes,
    )
    offset += 0.05
    if bounds:
        ax.text(
            1.05,
            offset,
            f"ceil((k+w)/w)/(k+w) new bound",
            color="blue",
            transform=plt.gca().transAxes,
        )
        offset += 0.05
        ax.text(
            1.05,
            offset,
            f"(k+2w-1)/(w*(k+w)) continuation",
            color="purple",
            transform=plt.gca().transAxes,
        )
        offset += 0.05

    sns.lineplot(
        x="k",
        y="density",
        hue="Minimizer type",
        data=df,
        legend="full",
        marker=".",
        dashes=False,
        ax=ax,
    )
    sigma = df.sigma.unique()[0]
    ax.set_title(f"Minimizer density (σ={sigma}, w={w})")
    ax.set_xlabel("Kmer length k")
    ax.set_ylabel("Density")
    ax.set_yscale("log", base=2)
    ax.set_ylim(ymin, ymax)
    ax.set_yticks([2 / (w + 1), 1 / w], [f"2/(w+1)", f"1/w"])
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")

    fig.savefig(f"{name}.svg", bbox_inches="tight")
    # fig.savefig(f"{name}.png", bbox_inches="tight")


df = read()
plot(df, "background", False)
plot(df, "new-bound", True)

print("done")
