# version: 0.10
#
# Neu:        createFile: Generiert eine Tex-Datai, die die Struktur und die Wichtiste teilen
#                         von den Text hat
# 
# Bald:
#             Eine Einfache 'Interface'
# Pending:
#             Sentence processing -> Relative sentence, brackets...
#             Eine Vernunftige relevanceFunction


import re, sys
from steffen import getwordpriority
from fileCreator import textGenerator
from createSlides import writeSlides
from operator import itemgetter
from nltk.corpus import brown, wordnet as wn
from math import log
from oldmain import textsummary1
import pickle
import GUIMain
from PyQt4 import QtGui


###############

# Global variables

##############

app = QtGui.QApplication(sys.argv) 
app.setStyle("plastique")
dialog = GUIMain.MyDialog()
dialog.show()
app.exec_()
guiText = unicode(GUIMain.entryText)

dataSlides = {} 
dataSlides['author'] = GUIMain.authors
dataSlides['title'] = GUIMain.title
dataSlides['institute'] = GUIMain.institute
dataSlides['mail'] = GUIMain.mail
dataSlides['date'] = GUIMain.date
dataSlides['subTitle'] = GUIMain.subtitle

 
parameter= {}
parameter['keyWordPriority'] = GUIMain.keyWordPriority
parameter['numberOfSlides'] = GUIMain.numberOfSlides
parameter['numberOfSlides'] =  parameter['numberOfSlides'] - 5

parameter['charactersProSlide'] = GUIMain.charactersPerSlide
parameter['completePath'] = str(GUIMain.dirName)+'/'
#parameter['completePath'] = 'Texte/einsteins_brains/'


# Numbers slides

abbrs = ['e.g.','etc.']


##
	
#text = open(location + folder + '/texto.txt')
#texto = '\n\n' + text.read()
#text.close()
#text = texto



##

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
            words[word.lower()] = words[word.lower()] + (1.0/sum_words) # Gefaellt mir nicht
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
    


#######################


### getSections

# Findet Teilen von dem Text die Vermutlich Titeln sind

def getSections(text,biggies,boldies):
    
    print '#################Start Finding Sections####################'

    possibleTitles = []

    for element in boldies: # Should also be done with biggies?
        if element[0] in text and len(element[0]) >= 5:
            possibleTitles += [(element[0],text.index(element[0]))]
    possibleTitles = sorted(set(possibleTitles), key=itemgetter(1))
    for element in possibleTitles: print element            
    print '#################Sections Found####################'
    return possibleTitles



## getStructure

# Teilt den Text nach dem Vermutlichen Titeln (titles)

def getStructure(titles,text):
    listTitles = [[('',-1)]]
    listText = []

    for index in range(len(titles)):
        if listTitles[-1][-1][1] + 1 == titles[index][1]:
            listTitles[-1] += [titles[index]]
        else:
            listTitles += [[titles[index]]]

    for element in listTitles:
        if len(element) >= 4:
            listTitles.remove(element)

    for index in range(len(listTitles)-1):
        listText += [text[listTitles[index][-1][1]+1:listTitles[index+1][0][1]-1]]
    listText += [text[listTitles[-1][-1][1]+1:]]


    structure = []
    for index in range(len(listTitles)):
        structure += [(listTitles[index],listText[index])]


    return structure,listTitles

############################

#LinestoString

############################

def LinestoString(completePath,textLines,sections):
    stringText = ''
    filePath = completePath + 'texto.txt'
    filePath1 = completePath + 'texto1.txt'
    try:
        fileObject = open(filePath,'w')
        fileObject1 = open(filePath1,'w')
    except IOError:
        print 'Error:\nDirectory was Not Found - Please check the location'
    for section in sections:
        fileObject.write('#>\n')
        stringText += '#>\n'
        for element in section[1]:
            if len(element) >= 4:
                fileObject.write(element + '\n')
                stringText += element + '\n'
            else:
                fileObject.write('\n')
                stringText += '\n'
        fileObject.write('<#\n')
        stringText += '<#\n'
#        fileObject1.write('#>\n')
    stringText = ''.join(re.split('(?<=[a-z])\- *\n *(?=[a-z])',stringText))
    stringText = ''.join(re.split('(?<=\n) +(?=[A-Za-z0-9])',stringText))
    fileObject1.write(stringText)

    fileObject.close()

    fileObject1.close()
    
    return stringText

###################################
    
# Main 

###################################

def textsummary(textString):
  realwordfreq = getwordpriority(textString)
  x = textsummary1(textString,realwordfreq,dataSlides,parameter)

if __name__ == '__main__':

	if guiText == "": 

	        completePath = parameter['completePath'];
	
	        x = textGenerator(completePath)
	        nBoldies = x.boldies
	        
	        nBiggies = x.biggies
	        
	        textLines = x.textList
	
	        sections = getSections(textLines,nBiggies,nBoldies)
	        
	        structure, nListTitles = getStructure(sections,textLines)
	
	        textString = LinestoString(completePath,textLines,structure)
	
	        textString = re.sub(r"\(.*?\)","",textString)
	        realwordfreq = getwordpriority(textString)
	
	        y = writeSlides(dataSlides,nListTitles,textString,realwordfreq,parameter)

	else:
		textsummary(guiText)
