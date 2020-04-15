import sys
import pandas as pd
import spacy
from spacy_langdetect import LanguageDetector

src = sys.argv[1]
sentences = []
with open('res_{}.txt'.format(src)) as textfile:
    for x in textfile:
        x = x.strip()
        sentences.append(x)

def postprocessor(sentence):
  s = sentence.split("▁")
  s = ["".join(i.split()) for i in s]
  return " ".join(s)

sentences = [postprocessor(sentence) for sentence in sentences]
sentences = [sentence[1:] if sentence[0] == " " else sentence for sentence in sentences]

data = pd.read_csv("{}_en_pairs.csv")
data["translation"] = sentences
data["language"] = src

for i in range(len(data)-1,-1,-1):
  if data["translation"][i].find("==") != -1:
    data = data.drop(i).reset_index().drop("index",axis=1)
for i in range(len(data)):
  data["en"][i] = " ".join(data["en"][i].split())
  data["translation"][i] = " ".join(data["translation"][i].split())

nlp = spacy.load("en")
nlp.add_pipe(LanguageDetector(), name="language_detector", last=True)
for idx in range(len(data)-1,-1,-1):
  s = data[src][idx]
  e = data["en"][idx]
  t = data["translation"][idx]
  lang1 = nlp(s)
  if lang1._.language["language"] != src:
    data = data.drop(idx).reset_index().drop("index",axis=1)
    continue
  lang2 = nlp(e)
  if lang2._.language["language"] != "en":
    data = data.drop(idx).reset_index().drop("index",axis=1)
    continue
  lang3 = nlp(t)
  if lang3._.language["language"] != "en":
    data = data.drop(idx).reset_index().drop("index",axis=1)

data.to_csv("WikiNLI_{}.csv".format(src))