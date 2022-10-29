#!python3

import seaborn as sns
import matplotlib.pyplot as plt

ps = []

while True:
    try:
        x = int(input())
        if x > 7000000:
            ps.append(x)
    except:
        break

#ps = ps[:1000]

p = sns.histplot(ps, bins = 200)
#p = sns.histplot(ps, bins=200)

plt.show()
