#!/usr/bin/python
from __future__ import division
from itertools import *
from collections import defaultdict
import re
import operator

class HMM(object):

	def __init__(self, f):
		self.emission_counts = defaultdict(int)
		self.word_counts = defaultdict(int)
		self.ngrams = dict.fromkeys([1,2,3], {})
		self.tags = set()

		for line in f:
			sline = line.strip().split()
			count = float(sline[0])
			key = tuple(sline[2:])
			tag = key[0]
			self.tags.add(tag)
			ngram = re.compile("^([1-3])-GRAM$")

			if sline[1] == "WORDTAG":
				word = key[1]
				self.emission_counts[key] = count
				self.word_counts[word] += count
			elif ngram.match(sline[1]):
				self.ngrams[int(sline[1][0])][tag] = count

	def emission_prob(self, word, tag):
		return (self.emission_counts[(tag,word)]/self.ngrams[1][tag])

	def replace_word(self, word):
		if self.word_counts[word] < 5:
			return "_RARE_"
		else:
			return word

	def get_words(self):
		return self.word_counts.keys()

	def get_word_count(self,word):
		return self.word_counts[word]
				
def replace_infreq_words(hmm, inpf, outf):
	for line in inpf:
		if line == "\n":
			outf.write(line)
		else:
			sline = line.strip().split()
			word = sline[0]
			outf.write(" ".join([hmm.replace_word(word), " ".join(sline[1:]), "\n"]))

def read_sentences(f):
	sentence = []
	for line in f:
		if line != "\n":
			sentence.append(line.strip().split()[0])
		else:
			yield sentence
			sentence = []

def simple_tagger(hmm, word):
	probs = defaultdict(float)
	for tag in hmm.tags:
		if word in hmm.get_words():
			probs[(word,tag)] = hmm.emission_prob(word, tag)
		else:
			probs[(word,tag)] = hmm.emission_prob("_RARE_", tag)			
	maxval = max(probs.iteritems(), key=operator.itemgetter(1))[1]
	argmax = [k[1] for k,v in probs.items() if v==maxval]
	return argmax

###Usage example###
with open("gene.ncounts", "r") as f, open("gene.train", "r") as train, open("gene.ntrain", "w") as ntrain:
	hmm = HMM(f)

#Mapping infrequent words to _RARE_ keyword
#replace_infreq_words(hmm, train, ntrain)

with open("gene.dev", "r") as test:
  for sentence in read_sentences(test):
 		for word in sentence:
 		  	print word, "".join(simple_tagger(hmm, word))
 		print ''
		
