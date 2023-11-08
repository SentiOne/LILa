import sys
import csv
import json

lcc_in_file = "spa_news_2022_30K-sentences.txt"
json_out_file = "lcc_corpus_es.json"
verbose = True

txts = []
for row in csv.reader(open(lcc_in_file),delimiter="\t"):
  txts.append(row[1])
json.dump(txts,open(json_out_file, "w"), ensure_ascii=False, indent=2)

if verbose:
    print("saved {}-document corpus to {}.".format(len(txt), json_out_file))

