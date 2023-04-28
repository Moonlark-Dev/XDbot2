# XDbot2 develop 230428210210

import json

data = json.load(open("data/reply.images.json", encoding="utf-8"))

def parse(group, is_review = False):
    if not is_review:
        for i in range(len(data[group])):
            data[group][i] = data[group][i].split("url=")[-1].replace("]", "")
    else:
        for key in list(data[group].keys()):
            data[group][key] = data[group][key].split("url=")[-1].replace("]", "")

for g in ["A", "B", "C"]:
    parse(g)
parse("review", True)

json.dump(data, open("data/reply.images.json", "w", encoding="utf-8"))
    
