import sys
import json
import csv
from content_processor import ContentProcessor

src = sys.argv[1]
trg = "en"

file_src = "WikiMatrix.{}-{}.txt.{}".format(src,trg,src)
file_trg = "WikiMatrix.{}-{}.txt.{}".format(src,trg,trg)
file_score = "WikiMatrix.{}-{}.txt.score".format(src,trg)

pairs = []
with open(file_src) as textfile1, open(file_trg) as textfile2, open(file_score) as textfile3: 
    for x, y, z in zip(textfile1, textfile2, textfile3):
        x = x.strip()
        y = y.strip()
        z = z.strip()
        pairs.append((x,y,z))
# Filer out the sentences with less than 5 tokens or larger than 120 tokens
for i in range(len(pairs)-1,-1,-1):
  if len(pairs[i][0].split()) > 120 or len(pairs[i][0].split()) <=4:
    pairs.pop(i)
# Load preprocessor
services = {}
with open("service.json", 'r') as configfile:
    services = json.load(configfile)
config = services[src][trg]
contentprocessor = ContentProcessor(
            						src,
            						trg,
            						sourcebpe=config.get('sourcebpe'),
            						targetbpe=config.get('targetbpe'),
            						sourcespm=config.get('sourcespm'),
            						targetspm=config.get('targetspm')
        							)

with open("{}_en_pairs.csv".format(src), "a", newline='') as datacsv:
    csvwriter = csv.writer(datacsv, dialect=("excel"))
    csvwriter.writerow(["score",src,"en"])
    for s,t,score in pairs:
        csvwriter.writerow([score,s,t])

sentences = [contentprocessor.preprocess(pair[0]) for pair in pairs]
with open('input_{}.txt'.format(src), 'w') as f:
    for _list in sentences:
        for _string in _list:
            f.write(_string + ' ')
        f.write('\n')