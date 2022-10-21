import json

with open("results.json") as f:
    data = json.load(f)

max_score = max(data.values())

my_rank = {}

counter = 1
for city, score in sorted(data.items(), key=lambda item: item[1], reverse=True):
    print("|", counter, "|", city, "|", round(score, 2), "|")
    my_rank[city] = counter
    counter += 1


parsed_walk_scores = []

with open("walk_score.csv") as f:
    for line in f.readlines():
        city, state, score = line.split(",")[:3]
        city = city.strip().lower().replace(" ", "-").replace(".", "")
        state = state.strip().lower()
        score = float(score.strip())

        parsed_walk_scores.append((city, state, score))

parsed_walk_scores.sort(key= lambda x: x[2], reverse=True)
print(parsed_walk_scores)

walk_rank = []
difference = []
labels = []

counter = 1
for city, state, score in parsed_walk_scores:
    if city + " " + state in data:
        print(city, counter - my_rank[city + " " + state])
        walk_rank.append(counter)
        difference.append(counter - my_rank[city + " " + state])
        labels.append(city)
        
    counter += 1

print(difference)

import numpy as np
import matplotlib.pyplot as plt
 
  
# creating the dataset

fig, ax = plt.subplots()

# creating the bar plot
plt.bar(walk_rank, difference)

ax.tick_params(axis='both', which='major', labelsize=16)
ax.tick_params(axis='both', which='minor', labelsize=16)
 
plt.xlabel("Ranking in Walk Score", fontsize=26)
plt.ylabel("Difference between my ranking and Walk Score ranking", fontsize=26)
plt.title("Comparing my walkability ranking for top 100 cities to Walk Score", fontsize=26)
plt.show()