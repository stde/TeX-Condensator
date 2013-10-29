# -*- coding: cp1252 -*-

from operator import itemgetter


################################    

# Text Structure

################################


debug = 0

connectors = ['first','firstly','secondly','finally','lastly'
              'important','striking'
               'Furthermore', 'furthermore', 'moreover','Moreover',
              'Therefore',
               'therefore', 'thus', 'hence','Thus','Hence',
              'Consequently', 'consequently', 'otherwise', 'else',
                
               'besides', 'however', 'However', 'Nevertheless', 'nevertheless', 'nonetheless', 
                
              'example', 'instance' ]


# Connector shuld be imported

import re
from operator import itemgetter


### importantSentences

def importantSentences(tree):
       listSentences = []
       for paragraph in tree:
              for sentence in paragraph[0]: listSentences = listSentences + [sentence]
       importantSentences = sorted(listSentences,key=itemgetter(1), reverse=True)[:3]
       return importantSentences

### getSentences

def getSentence(parags):
       parags = re.split('\s*',parags)
       parags = ' '.join(parags)
       sentences = re.split('(?<=(?:\?|\.|!)) (?=[A-Z0-9\(])',parags)
#       sentences = re.split('\s*\.[^0-9]\s*',parags)
       return sentences
    

### getTree

def getTree(text,dictionary,parameters):
  sentences = getSentence(text)
  tupleListSentences = [] # Eine liste von tuplen: (_,_) -> (Sentence,Wert)
  for sentence in sentences:
      valueSentence = relevanceSentence(sentence,dictionary,parameters)
      tupleListSentences += [(sentence,valueSentence)]
  return tupleListSentences

### relevanceSentence

def relevanceSentence(sentence,dictionary,parameter):
#      Bis jetzt nur ein Durchschnitt
       listValues = []
       listWords = re.split(' ',sentence)
       
       # number of keywords in sentence
       count = 0
       for word in listWords:
                if word in dictionary:
                     listValues = listValues + [dictionary[word]]
	      # keyword found
		if word in connectors:
		     count = count + 1;
		     if debug == 1:
		     	print 'found keyword' + word + 'in sentence' + sentence;
		

       try:
              if  len(listValues) > 14:
                   value = sum(listValues) / (len(listValues)+5)
              else:
                   value = sum(listValues) / len(listValues)


	      # calculate keyWordPriority

	      value = value*(1 + ( parameter['keyWordPriority'] *count));
       except ZeroDivisionError:
              value = 0
       return value



## relevanceParagraph

def relevanceParagraph(paragraph):
#      Bis jetzt nur ein Durchschnitt
       value = 0
       for sentence in paragraph:
              value = value + sentence[1]
       try:
              value = value / len(paragraph)
       except ZeroDivisionError:
              value = 0
       return value


### importantWords

def importantwords(listSentences):
       importantSentences = sorted(listSentences,key=itemgetter(1), reverse=True)[:3]
       return importantSentences


###################

class treeFinder:
       def __init__(self,text,dictionary,parameters):
              listSentences = getTree(text, dictionary,parameters)
#              importantSentences = importantwords(listSentences)
              self.listSentences = listSentences
