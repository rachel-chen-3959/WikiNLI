import sys
import re
import json
import pandas as pd
from collections import defaultdict
from nltk.parse import CoreNLPParser
import numpy as np

'''
Load data from json file
'''
data_file = sys.argv[1]
f = open(data_file,"r")
data = []
for i in f:
    data.append(json.loads(i.strip()))
data = pd.DataFrame(data)
data = pd.concat([data[data["label"] == "n"],data[data["label"] == "e"],data[data["label"] == "c"]])
data = data.reset_index()
labels = ["n","e","c"]
parts = ["all","hypothesis","premise"]
parser = CoreNLPParser(url='http://localhost:9000')

'''
Evaluation about Words
'''
def tokenize(string):
    string = re.sub(r'\(|\)', '', re.sub(r'[^\w\s]','',string.lower()))
    return string.split()

def pmi(data_part,label):
    data_temp = data[data["label"]==label]
    if data_part == "all":
        data_text = data["premise"].tolist() + data["hypothesis"].tolist()
        label_text = data_temp["premise"].tolist() + data_temp["hypothesis"].tolist()
    else:
        data_text = data[data_part].tolist()
        label_text = data_temp[data_part].tolist()
    data_word = []
    label_word = []
    word_freq = defaultdict(int)
    for s in data_text:
        data_word += tokenize(s)
    for s in label_text:
        label_word += tokenize(s)
    p_x_y = Counter(label_word)
    p_x = Counter(data_word)
    res = defaultdict(int)
    for w in p_x_y:
        res[w] = np.log10(p_x_y[w]/len(label_word)/(p_x[w]/len(data_word)))
    for s in data_temp["hypothesis"].tolist():
        words = set(tokenize(s))
        for w in res:
            if w in words:
                word_freq[w] += 1
    return sorted([(res[w],word_freq[w],w) for w in res],reverse=True)[:10]

for label in labels:
	df = data[data["label"] ==  label].reset_index()
	l = 0
	for i in range(len(df)):
    	l1 = set(tokenize(df["hypothesis"][i]))
    	l2 = set(tokenize(df["premise"][i]))
    	l += len(l1-l2)
    print("label:{}, token counts in hypothesis but not in premise: {}".format(label,str(l)))


for part in parts:
	for label in labels:
		print(pmi(part,label))

		df = data[data["label"] ==  label].reset_index()
		if part == "all":
			sentences = df["hypothesis"].to_list() + df["premise"].to_list()
		else:
			sentences = df[part].to_list()
		l = 0
		for sentence in sentences:
    		l += len(tokenize(sentence))
    	print("part:{}, label:{}, mean token count: {}".format(part, label, str(l/len(df))))

    	l = set()
		for i in premise:
    		l |= set(tokenize(sentence))

for part in parts:
	if part == "all":
		continue
	else:
		sentences = data[part].to_list()
    f = open("{}_{}".format(data_file, part),"a")
    for sentence in sentences:
    p = list(parser.parse(sentence.split()))
    for w in p:
        f.write(' '.join(str(w).split()) )
    f.write("\n")
hypothesis = []
f = open("{}_hypothesis".format(data_file), 'r')
for i in f:
    hypothesis.append(i)
premise = []
f = open("{}_premise".format(data_file), 'r')
for i in f:
    premise.append(i)
df = pd.DataFrame([],index=list(tags_to_results.keys()))
tags_to_results = defaultdict(list)
def log(tag, is_correct, label):
    tags_to_results[tag].append((is_correct, label))

def find_1st_verb(str1):  #find ptb verb codings for first verb from root of sentence
    findy=str1.find('(VB')
    if findy >0:
        return str1[findy:].split()[0]
    else: 
        return ''

def tense_match(str1,str2):   # this function test for tense match, by finding the first verb and checking it against the second verb occurence
    result=find_1st_verb(str1)
    if len(result)>0:
        findy2=str2.find(result)
        return findy2>0
    else:
        return False
ptbtags={"(MD":"modal","(W":"WH","(CD":"card","(PRP":"pron","(EX":"exist","(IN":"prep","(POS":"'s"}
if True:
    i = 0
    while i < len(data):
        label = data["label"][i]
        if label in ["e", "c", "n"]:
            p1 = premise[i]
            p2 = hypothesis[i]
            parses = p1 + " " + p2
            correct = 'correct' # this needs to be supplied from the model outputs

            log("label-" + label, correct, label)


            if "n't" in parses or "not" in parses or "none" in parses or "never" in parses or "neither" in parses or "nor" in parses:  # add in un- and non- :/
                log('neg-all', correct, label)
                if ("n't" in p2 or "not" in p2 or "none" in p2 or "never" in p2 or "neither" in p2 or "nor" in p2) and not ("n't" in p1 or "not" in p1 or "none" in p1 or "never" in p1 or "neither" in p1 or "nor" in p1):
                    log('neg-hyp-only', correct, label)


            if "a" in parses or "the" in parses or "these" in parses or "this" in parses or "those" in parses or "that" in parses: 
                log('det-all', correct, label)
                if ("a" in p2 or "the" in p2 or "these" in p2 or "this" in p2 or "those" in p2 or "that" in p2) and not ("a" in p1 or "the" in p1 or "these" in p1 or "this" in p1 or "those" in p1 or "that" in p1):
                    log('det-hyp-only', correct, label)
            for key in ptbtags:
                if key in parses:
                    log(ptbtags[key]+'_ptb_all', correct, label)
                if (key in p2) and not (key in p1):
                    log(ptbtags[key]+'_ptb_hyp_only', correct, label)

            if ("(NNS"  in p2) and ("(NNP" in p1):
                log('plural-premise-sing-hyp_ptb', correct, label)
            if ("(NNP"  in p2) and ("(NNS" in p1):
                log('plural-hyp-sing-premise_ptb', correct, label)

            if tense_match(p1,p2):
                log('tense_match', correct, label)

            if "(UH" in parses: 
                log('interject-all_ptb', correct, label)
                if ("(UH"  in p2) and not ("(UH" in p1):
                    log('interject-hyp-only_ptb', correct, label)

            if "(FW" in parses: 
                log('foreign-all_ptb', correct, label)
                if ("(FW"  in p2) and not ("(FW" in p1):
                    log('foreign-hyp-only_ptb', correct, label)


            if "(JJ" in parses: 
                log('adject-all_ptb', correct, label)
                if ("(JJ"  in p2) and not ("(JJ" in p1):
                    log('adject-hyp-only_ptb', correct, label)

            if "(RB" in parses: 
                log('adverb-all_ptb', correct, label)
                if ("(RB"  in p2) and not ("(RB" in p1):
                    log('adverb-hyp-only_ptb', correct, label)

            if "(JJ" in parses or "(RB" in parses: 
                log('adj/adv-all_ptb', correct, label)
                if ("(JJ"  in p2 or "(RB" in p2) and not ("(JJ" in p1 or "(RB" in p1):
                    log('adj/adv-hyp-only_ptb', correct, label)

            if "(RBR" in parses or "(RBS" in parses or "(JJR" in parses or "(JJS" in parses: 
                log('er-est-all_ptb', correct, label)
                if ("(RBR"  in p2 or "(RBS" in p2 or "(JJR" in p2 or "(JJS" in p2) and not ("(RBR" in p1 or "(RBS" in p1 or "(JJR" in p1 or "(JJS" in p1):
                    log('er-est-hyp-only_ptb', correct, label)
#########################

            s1 = p1[0:8] == "(ROOT (S"
            s2 = p2[0:8] == "(ROOT (S" 
            if s1 and s2:
                log('syn-S-S', correct, label)
            elif s1 or s2:
                log('syn-S-NP', correct, label)
            else:
                log('syn-NP-NP', correct, label)

            for keyphrase in ["much", "enough", "more", "most", "every", "each", "less", "least", "no", "none", "some", "all", "any", "many", "few", "several"]:  # get a list from Anna's book, think more about it
                if keyphrase in p2 or keyphrase in p1:
                    log('template-quantifiers', correct, label)
                    break

            for keyphrase in ["know", "knew", "believe", "understood", "understand", "doubt", "notice", "contemplate", "consider", "wonder", "thought", "think", "suspect", "suppose", "recognize",  "recognise", "forgot", "forget", "remember",  "imagine", "meant", "agree", "mean",  "disagree", "denied", "deny", "promise"]:
                if keyphrase in p2 or keyphrase in p1:
                    log('template-beliefVs', correct, label)
                    break

            for keyphrase in ['if']:
                    if keyphrase in p2 or keyphrase in p1:
                        log('template-if', correct, label)
                        break

            for keyphrase in ["time", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "morning", "night", "tomorrow", "yesterday", "evening", "week", "weeks", "hours", "minutes", "seconds" "hour", "days", "years", "decades", "lifetime", "lifetimes", "epoch", "epochs", "day", "recent", "recently", "habitually", "whenever", "during", "while", "before", "after", "previously", "again", "often", "repeatedly", "frequently", "dusk", "dawn", "midnight", "afternoon", "when", "daybreak", "later", "earlier", "month", "year", "decade", "biweekly", "millenium", "midday", "daily", "weekly", "monthly", "yearly", "hourly", "fortnight", "now", "then"]:
                    if keyphrase in p2 or keyphrase in p1:
                        log('template-timeterms', correct, label)
                        break

            for keyphrase in ["too", "anymore", "also", "as well", "again", "no longer", "start", "started", "starting", "stopping", "stop", "stopped", "regretting", "regret", "regretted", "realizing", "realize", "realized", "aware", "manage", "managed", "forgetting", "forget", "forgot", "began", "begin", "finish", "finished", "finishing", "ceasing", "cease", "ceased", "enter", "entered", "entering", "leaving", "leave", "left", "carry on", "carried on", "return", "returned", "returning", "restoring", "restore", "restored", "repeat", "repeated", "repeating", "another", "only", "coming back", "come back", "came back"]:
                    if keyphrase in p2 or keyphrase in p1:
                        log('template-presupptrigs', correct, label)
                        break

            for keyphrase in ["although", "but", "yet", "despite", "however", "However", "Although", "But", "Yet", "Despite", "therefore", "Therefore", "Thus", "thus"]:
                    if keyphrase in p2 or keyphrase in p1:
                        log('template-convo-pivot', correct, label)
                        break                          

        i += 1
df["all"] = 0
for i in tags_to_results.keys():
    df["all"][i] = len(tags_to_results[i])/len(data)
for label in labels:
	df[label] = 0.0
	for i in tags_to_results.keys():
			df[label][i] = len([j for j in tags_to_results[i] if j[1] == label])/len(tags_to_results["label-{}".format(label)])
df.to_csv("{}_liguistic".format(data_file))

cnt = 0
for i in range(len(data)):
    if set([data["label1"][i],data["label2"][i],data["label3"][i],data["label4"][i],data["label5"][i]]) != set(data["gold_label"][i]):
        cnt += 1
print("Pairs w/ unanimous gold label: {}".format(str(cnt / len(data))))

cnt = 0
for i in range(len(data)):
    for j in range(1,6):
        if data["label"+str(j)][i] == data["gold_label"][i]:
            cnt += 1
print("Individual annotator label agreement: {}".format(str(cnt / len(data) / 5)))





