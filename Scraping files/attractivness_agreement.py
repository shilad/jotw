#!/usr/bin/python -O
import random
from collections import defaultdict
from csv import DictReader
import numpy as np


ratings = defaultdict(list)
all_ratings = []

for row in DictReader(open('dat/Batch_2887867_batch_results.csv')):
    vt = row['Answer.videoType']
    att = row['Answer.attractiveness']
    url = row['Input.video_url']
    if not vt:
        att = int(att)
        ratings[url].append(int(att))
        all_ratings.append(int(att))

valid = [url for url in ratings.keys() if len(ratings[url]) >= 3]
print(len(ratings), len(valid))
cf = np.zeros((7, 7), dtype=np.int64)

N = 10000
variance = 0.0
variance_null = 0.0

for i in range(N):
    url = random.choice(valid)
    (r1, r2) = random.sample(ratings[url], 2)
    cf[r1 + 3][r2 + 3] += 1
    variance += (r1 - r2) ** 2.0

    (r1, r2) = random.sample(all_ratings, 2)
    variance_null += (r1 - r2) ** 2.0

print(np.sqrt(variance / N), np.sqrt(variance_null / N))

print(1.0 * cf / np.sum(cf))

import matplotlib.pyplot as plt
import numpy as np
heatmap = plt.imshow(cf, cmap='hot', interpolation='none')
plt.colorbar(heatmap)
plt.show()