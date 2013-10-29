# -*- coding: cp1252 -*-
# version: 0.11
#
# Neu:      connectors erhoehen sentence priority, debug variable zur besseren ausgabe 
# Neu:	    parameter for keywordPriority                         
# Neu:	    debug parameter

import re
from operator import itemgetter
from nltk.corpus import brown, wordnet as wn
from math import log
import pickle


keyWordPriority = 0.2;
debug = 1;


###

dataSlides = {}
dataSlides['author'] = 'TeX-Condensator'
dataSlides['institute'] = 'IKW'
dataSlides['mail'] = 'noone@uos.de'
dataSlides['date'] = 'Mai 2010'


##


text = open('text21.txt','r')
text = '\n\n' + text.read()


##

abbrs = ['e.g.','etc.']
connectors = ['first','firstly','secondly','finally','lastly'
              'important','striking'
               'Furthermore', 'furthermore', 'moreover','Moreover',
              'Therefore','innovation'
               'therefore', 'thus', 'hence','Thus','Hence',
              'Consequently', 'consequently', 'otherwise', 'else',
               
               'besides', 'however', 'However', 'Nevertheless', 'nevertheless', 'nonetheless', 
               'key', 
              'example', 'instance' ]





capitals = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
# input: string
# output: dictionary, words as keys, # of word as value

### makeWords

def makeWords(string):
    words = ' '.join(re.findall('[a-zA-Z]+',string))
    return words
    

##################################

# Priority Module

##################################


### getwords


def getwords(text):
    words = {}
    for abbr in abbrs:
        text = text.replace(abbr,'')
    all_words = re.findall('[A-Za-z]{3}[A-Za-z]+', text)
    sum_words = len(all_words)
    for word in all_words:
        if word.lower() in words:
            words[word.lower()] = words[word.lower()] + (1.0/sum_words) # Gefällt mir nicht
        else:
            words[word.lower()] = 1.0/sum_words
    return words
    
### comparetextcorpus

# compares frequency of words in text with frequency in corpus

def comparetextcorpus(relwordfreqtext):
    file = open("brown.txt")
    corpus = pickle.load(file)
    file.close()

    # upper and lower bound
    minn = 0;
    maxx = 0;

    for word in relwordfreqtext:
        if word in corpus:
            relwordfreqtext[word] = log(relwordfreqtext[word] / corpus[word])
        else:
            relwordfreqtext[word] = log(relwordfreqtext[word] / (1.0/1200000))


        # get new max and minumun
        if relwordfreqtext[word] > maxx:
          maxx = relwordfreqtext[word]

        if relwordfreqtext[word] < minn:
          minn = relwordfreqtext[word]        

   # norm values so that they are between 0 and 1
    for word in relwordfreqtext:
        relwordfreqtext[word] = ((relwordfreqtext[word]-minn) * (1/(maxx-minn)))


    return relwordfreqtext
    

### relevanceSentence

def relevanceSentence(sentence,dictionary):
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
	      value = value*(1 + (keyWordPriority*count));
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

### importantSentences
### get 3 sentences per Paragraphs


def importantSentences(tree,parameter):
       listSentences = []
       for paragraph in tree:
              for sentence in paragraph[0]: listSentences = listSentences + [sentence]
       count = 1
       i = 0
       while i < parameter['charactersProSlide']:
            importantSentences = sorted(listSentences,key=itemgetter(1), reverse=True)[:count]
            i = i + len(importantSentences[-1][0]);
            count = count +1
	#tupelsentence = []
	#for sentence in importantSentences
         #    index = listSentences.index(sentence)
          #   tuplesentence += [(index,sentence)] 
	 
       
       return importantSentences
             

################################    

# Text Structure

################################

### getSentences

def getSentence(parags):
       parags = re.split('\s*',parags)
       parags = ' '.join(parags)
       sentences = re.split('(?<=(?:\?|\.|!)) (?=[A-Z0-9\(])',parags)
#       sentences = re.split('\s*\.[^0-9]\s*',parags)
       return sentences
    

### getTree

def getTree(text,dictionary):
# Gegeben einen Text und eine Woertschaz teilt den Text in Absaetzen und Saetzen
# und berechnet ein Wert von jedem Satz und jedem Absatz
    listParagraph = re.split('(?<=\.)\s*?\n\s*?(?=[A-Z])',text) # Teil den Text in Paragraphen
    tuplePg = [] #(Der Text wird als eine Liste von Tupeln representiert: (Absatz,wert)
    for paragraph in listParagraph:
        sentences = getSentence(paragraph)
        tupleSentences = [] # Eine liste von tuplen: (_,_) -> (Sentence,Wert)
        for sentence in sentences:
            valueSentence = relevanceSentence(sentence,dictionary)
            tupleSentences = tupleSentences + [(sentence,valueSentence)]
        valueParagraph = relevanceParagraph(tupleSentences) # toca pillar
        tuplePg = tuplePg + [(tupleSentences,valueParagraph)]
    return tuplePg



### getSections

# Findet Teilen von dem Text die Vermutlich Titeln sind

def getSections(text):
    text = re.sub('[Aa][Bb][Ss][Tr][Rr][Aa][Cc][Tt]',r'\nAbstract\n',text)
    text = re.sub('[Kk][Ee][Yy] ?[Ww][Oo][Rr][Dd][Ss]',r'\nKeywords\n',text)
    resultSentences = None
    lenTitle = 50 # Wie lang ein titel sein darf
    while resultSentences == None and lenTitle > 10: # Mach die Implementation Stark bei 'iterating' ueber die Lenge ein Titel
        regularExp = (r'\n.{2,') + str(lenTitle) + (r'}?[^(:|.| |\n)] *\n')
        notRegText = re.findall(regularExp, text)
        indexes = []
        sections = '#'
        for index in range(len(notRegText)):
            possibleSection = ' '.join(re.findall('[A-Za-z]{1}[A-Za-z]+', notRegText[index])) # Versuch die Komischen Teilen als Worter zu betrachten
            if len(possibleSection) > 2 and possibleSection[0] in capitals: # ignoriert Worter die nicht mit grosse buchstaben anfangen
                sections = sections + '#' + possibleSection
                indexes = indexes + [index]
        sections = sections + '#'
        if float(len(sections)) / float(len(text)) < 0.02: # Die 'Titles' duerfen nicht mehr als 2 Prozent des Textes sein
            resultSentences = []
            for index in indexes: resultSentences = resultSentences + [notRegText[index]] # Trick um den Text zu behalten!
        else:
            lenTitle = lenTitle - 10
    return resultSentences


## getStructure

# Teilt den Text nach dem Vermutlichen Titeln (titles)

def getStructure(titles,text):
       formatTitles = []
       for title in titles: formatTitles = formatTitles + [makeWords(title)]
       newTitles = []
       for title in titles: # Ein Trick um Sachen rauszukicken!
           if formatTitles.count(makeWords(title)) > 1:
               continue
           else:
               newTitles = newTitles + [title]
       titles = newTitles
       lenText = len(text)
       structure = []
       startString = '(.*?)' + titles[0] # Generiert ein Regularexpression
       #structure = structure + [['start',re.search(startString,text,re.DOTALL).groups()[0]]]
       for index in range(len(titles) - 1):
              regularExp = titles[index] + '(.*?)' + titles[index+1]
              try:
                  structure = structure + [[titles[index],re.search(regularExp,text,re.DOTALL).groups()[0]]] # Generiert probleme manchmal
              except AttributeError:                
                  structure = structure + [[titles[index],'\#\#']]

       endString = titles[-1] + '(.*)'
       try:
           structure = structure + [[titles[-1],re.search(endString,text,re.DOTALL).groups()[0]]]
       except AttributeError:
           structure = structure + [titles[-1],'##']
        
       newStructure = [] + [structure[0]] # Verbessert die geschaffene Struktur

       for index in range(1,len(structure),1):   
           if (len(structure[index][1])) / float(len(text)) > 0.01:
               newStructure = newStructure + [structure[index]]
           else:
              newStructure[-1][1] =  newStructure[-1][1] + structure[index][0] + structure[index][1]

       lastTitles = []
       for index in newStructure: lastTitles = lastTitles + [index[0]]
           
       return newStructure,lastTitles


#########################            

# Slides Generator

#########################

### createOpening

def createOpening(data):
       startSlides = ''
       startSlides = startSlides + (r'''
% titlepage-demo.tex
\documentclass{beamer}
\usepackage{color}
\usepackage{subfigure}
\usepackage{hyperref}
\usetheme{Copenhagen}
''')
       parameters =('''
\\title{%s}
\\subtitle{%s}
\\author{%s}
\\institute{
  %s\\\\[1ex]
  \\texttt{%s}
  }
  ''' % (data['title'], data['subTitle'], data['author'],data['institute'],data['mail']))
       date = (r'\date[') + data['date'] + (r']{') + data['date'] + (r'}')
       startSlides = startSlides + parameters + date 
       startSlides = startSlides + (r'''
\begin{document}
%--- the titlepage frame -------------------------%
\begin{frame}[plain]
  \titlepage
\end{frame}
''')
       return startSlides


### createOutline

def createOutLine(sections):
       outLineString = (r'''%--- the presentation begin here -----------------%
\begin{frame}
\frametitle{Outline}
  
\begin{itemize}
''')
       for section in sections:
              outLineString = outLineString + (' \item %s \n' % section)

       outLineString = outLineString + (r'''\end{itemize}
\end{frame}
%%
''')
       return outLineString
       

### createBody


def createBody(structure,dictionary,parameter):
       body = '%%%'
       for section in structure:
              tree = getTree(section[1],dictionary)
              relevantSentences = importantSentences(tree,parameter)
              contentSlide = ''
              for sentence in relevantSentences:
                  contentSlide = contentSlide + (r'''
  \item  ''') + sentence[0]

              body = body + (r'''
\begin{frame}[plain]
''')
              body = body + ('\\frametitle{%s}' % section[0])
              body = body + (r'''
 \begin{itemize}''') + contentSlide + (r'''

 \end{itemize}

\end{frame}

%%%
''')
       return body


### createFile

def createFile(data,sections,structure,dictionary,parameter):
       slides = open("presentationold.tex","w")
       fileString = ''
       startSlides = createOpening(data)
       outLine = createOutLine(sections)
       bodySlides = createBody(structure,dictionary,parameter)
       endSlides = (r'\end{document}')
       fileString = fileString + startSlides + outLine + bodySlides + endSlides
       slides.write(fileString)
       slides.close()
       print unicode(fileString)
       
###################################

# Main 

###################################
class textsummary1:
	def __init__(self,text, realwordfreq,dataSlides,parameter):
    		text = re.sub(r'&','\&',text)
		treeStructure = getTree(text,realwordfreq)
    		sections = getSections(text)
    		structure, titles = getStructure(sections,text)        
    		createFile(dataSlides,titles,structure,realwordfreq,parameter)
    
