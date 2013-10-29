#!/usr/bin/python
# -*- coding: utf-8 -*-

from nltk.corpus import wordnet as wn

def define(word):
    for lemma in wn.lemmas(word):
        pretty_print_synset(lemma.synset,word)
    
def synonyms(word):
    synonyms = []
    for lemma in wn.lemmas(word):
        group = lemma.synset.lemma_names
        if word and (word in group):
           group.remove(word)
           group.insert(0,word)
        if len(group) > 1:
	   for synonym in group[1:]:
	       if '_' not in synonym:
	           synonyms.append(synonym)
    return synonyms

def antonyms(word):
    antonyms = []
    for lemma in wn.lemmas(word):
        for antonym in lemma.antonyms():
	    for word in antonym.synset.lemma_names:
		antonyms.append(word.replace('_',' '))
    return antonyms

def hypernyms(word):
    hypernyms = []
    for lemma in wn.lemmas(word):
        for hypernym in lemma.synset.hypernyms():
	    for word in hypernym.lemma_names:
	        if '_' not in word:
        		hypernyms.append(word)
    return hypernyms

def hyponyms(word):
    hyponyms = []
    for lemma in wn.lemmas(word):
        for hyponym in lemma.synset.hyponyms():
	    for word in hyponym.lemma_names:
		hyponyms.append(word.replace('_',' '))
    return hyponyms



class WordNetParser(object):
    def __init__(self):
	    pass
    
    def do_antonyms(self, word):
        return set(antonyms(word))

    def do_synonyms(self, word):
        return set(synonyms(word))

    def do_hypernyms(self, word):
        return set(hypernyms(word))

    def do_hyponyms(self, word):
        return set(hyponyms(word))



"""
wnp = WordNetParser()

print wnp.do_synonyms("help")
print wnp.do_antonyms("man")
print wnp.do_hypernyms("chair")
print wnp.do_hyponyms("boy")
"""
