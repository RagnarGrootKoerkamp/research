#!/usr/bin/env python3

from math import log, floor, ceil
import matplotlib.pyplot as plt


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
plt.plot(xs, [linear(x) for x in xs], label="Linear  $\,x$")
plt.plot(xs, [skew(x) for x in xs], label="Skewed $0.6\mapsto0.3$")
plt.plot(xs, [optimal(x) for x in xs], label="Optimal $x + (1{-}x)\ln(1{-}x)$")
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
plt.plot(xs, [bucket_sz(linear, x) for x in xs], label="Linear   $\,x$")
plt.plot(xs, [bucket_sz(skew, x) for x in xs], label="Skewed $0.6\mapsto0.3$")
plt.plot(
    xs, [bucket_sz(optimal, x) for x in xs], label="Optimal $x + (1{-}x)\ln(1{-}x)$"
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
plt.ylabel("Expected bucket size for $\lambda = 4$")
# Add horizontal grid lines
plt.grid(axis="y", lw=0.5, which="major")
plt.grid(axis="y", lw=0.5, which="minor", alpha=0.4)
# Add minor tickes lines every 1
plt.yticks(range(0, 12, 1), minor=True)

plt.savefig("plots/bucket-size.svg", bbox_inches="tight")
plt.close()
