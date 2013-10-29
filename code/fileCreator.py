#####################

# FILE CREATOR: Generates a plain text representation of the text
# This includes however information regarding format of the text (bold, cursive
# and size.


#####################



import urllib
import re
from operator import itemgetter
from collections import deque

###

#Global variables

#location = 'C:/Users/del.l/Documents/textos_prueba/'

##

# Creates a plain text give a directory where the HTM version of a PDF file was saved!

def createText(path):
    switch = None
    variable = 1
    textComplete = []
    italic = []
    boldies = []
    biggies = []
    sizeFonts = {}

    while switch == None:
              
       pageNumber = str(variable)
       for i in range(4-len(pageNumber)): pageNumber = '0' + pageNumber
       page = 'file:///' + path + 'pg_' + pageNumber + '.htm'
       page = path + 'pg_' + pageNumber + '.htm'
       
     #  print 'Analyzing:', page
       
       try:

# Generate a list representation of the text

              strongText, weakText, dictFonts, nBoldies, nBiggies = printHtml(page)

              boldies += nBoldies
              biggies += nBiggies

#Write the plain text data

              for textBox in strongText:

                     textComplete += [textBox[0][0]]
                     
                     for index in range(1,len(textBox)):

                            if textBox[index-1][2] == textBox[index][2]:
                                   textComplete[-1] += textBox[index][0]
                            else:
                                   textComplete += [textBox[index][0]]
              variable += 1
              
       except IOError:
              switch = 0

    return biggies, boldies, textComplete



def fontsAndLines(datai):

# Find all the lines in the Html and all the fonts:

       import urllib
       sock = urllib.urlopen(datai)
       htmlSource = sock.read()
       sock.close()

       ## Find the fonts

       fonts = re.findall('ft([0-9]+)\{font-style:([a-zA-Z]+);font-weight:([a-zA-Z]+);font-size:([0-9]+)px;',htmlSource)
       dictFonts = {}
       for element in fonts:
           dictFonts[element[0]] = {}
           dictFonts[element[0]]['style'] = element[1]
           dictFonts[element[0]]['weight'] = element[2]
           dictFonts[element[0]]['size'] = element[3]
           dictFonts[element[0]]['number'] = 0

       ## The lines are transformed into tuples (content, horizontal, vertical,font)

       allLines = re.findall('div.*?/div',htmlSource)
       dictLines = []

       for index in range(len(allLines)):
              try :
                     matchObject = re.search('top[:](?P<top>[0-9]+)[;]left[:](?P<left>[0-9]+)["][>][<]nobr[>][<]span class[=]["]ft(?P<font>[0-9]+)["][>](?P<content>.*?)[<][/]span[>]',allLines[index])
                     smallDict = matchObject.groupdict()
                     dictLines += [(smallDict['content'],int(smallDict['left']),int(smallDict['top']),int(smallDict['font']))]
                     dictFonts[smallDict['font']]['number'] += 1
              except AttributeError:
                     continue
       dictLines = sorted(dictLines,key=itemgetter(1))

       return dictFonts,dictLines


def getTextBoxes(dictLines):

## The lines are organized in text boxes, which are consecutive lines starting at the same horizontal line


       textBoxes = [[dictLines[0]]]
       variable = dictLines[0][1]  # This is a trick to allow small diffences is the horizontal distance without allowing a strair effect!
       for index in range(1,len(dictLines)):
           #PATAMETER!!!
              if abs(dictLines[index][1] - variable) <= 20 :
                     textBoxes[-1] = textBoxes[-1] + [dictLines[index]]
              else:
                     textBoxes = textBoxes + [[dictLines[index]]]
                     variable = dictLines[index][1]
       newTextBoxes = []

       # Sorting inside the textBoxes

       for element in textBoxes:
              newElement = sorted(element,key=itemgetter(2))
              newTextBoxes = newTextBoxes + [newElement]
       textBoxes = newTextBoxes
       
       return textBoxes



def microTextBoxes(element):

#Defines textboxes inside text boxes which haven't been worked on.
# Elements must be sorted!!!!!!!

              element = sorted(element, key=itemgetter(2))
              lengthElement = len(element)
              sumDistances = element[-1][2]- element[0][2] # The total vertical distance of a paragraph
              expectedValue = sumDistances / lengthElement              
              # Divides again inside the TextBoxes
              miniList = [[element[0]]]
              for index in range(1,len(element)):

# PARAMETER!!!!!!!!!!!!!!!!!!!!
    
                     if abs(element[index][2] - element[index-1][2]) <= float(expectedValue * 3): # If the difference between two lines is smaller that the expValue, it belongs to same group
                            # Something is shit in the last line!!!!!!
                            miniList[-1] = miniList[-1] + [element[index]]
                     else: # in other case open another group
                            miniList = miniList + [[element[index]]]
              return miniList



def getStrongWeakBoxes(textBoxes):

# Divides the textBoxes in weak and strong

       strongTextBox = []
       weakText = []
       for element in textBoxes:
                     microTextBox = microTextBoxes(element)

                     for index in microTextBox:
                            if len(index) < 10: #PARAMETER!!!!!!!!!!!!!!!!!
                                   weakText = weakText + index
                            else:
                                   strongTextBox = strongTextBox + [index]
       if len(strongTextBox) >= 2:
           coordinates = []
           for index in range(len(strongTextBox)):
               coordinates += [(strongTextBox[index][0][1],index,strongTextBox[index][0][2])]
           coordinates = sorted(coordinates)
           nCoordinates = [[coordinates[0]]]
           
           for index in range(1,len(coordinates)): # Merge together similar strong text boxes
######### Parameter!!!!!!!!!!!!
               if abs(nCoordinates[-1][0][0] - coordinates[index-1][0]) <= 40 and abs(nCoordinates[-1][0][2] - coordinates[index-1][2]) <= 40:
                   nCoordinates[-1] += [coordinates[index]]
               else:
                   nCoordinates += [[coordinates[index]]]

           nStrongTextBox = []
           for index1 in nCoordinates:
               microLista = []
               for index2 in index1:
                   microLista += strongTextBox[index2[1]]
               nStrongTextBox += microLista
               
       return strongTextBox, weakText


def depureTextBoxes(strongTextBoxInput, weakTextBoxInput):
        weakTextBox = weakTextBoxInput

        strongTextBox = strongTextBoxInput

        ediCoordinates = []

        elementWeakTextBox = []

        coordinates = []

        newCoordinate = []
        
        for index in range(len(strongTextBox)):
               coordinates += [(strongTextBox[index][0][1],strongTextBox[index][0][2],strongTextBox[index][-1][2]),index] # A list with the coordinates: horizontal, vertial 1, vertical last element, index
               coordinates = sorted(coordinates)

        for sentence in weakTextBox:
            """
            # IF the sentence is in the vertical limits of a strong box, then the coordinates of the strong box are saved in newCoordinate
            
            newCoordinates = []

            variable = 0

            while variable <= len(coordinates)-1:
                if sentence[1] >= coordinates[variable]:
                    smallCoordinates = sorted(coordinates[variable:],key=itemgetter(1))
                    variable = 0
                    while variable <= len(smallCoordinates)-1:
                        if sentence[2] <= smallCoordinates[variable][1] * 1.20:
                            strongTextBox[smallCoordinates[variable][3] += [sentence]
                            variable = len(smallCoordinates)
                        else:
                            variable += 1
                    variable = len(coordinates)
                else:
                    variable += 1
                        
            """                    

            for strongBox in strongTextBox:

            ################ Parameter ######################
                 if strongBox[0][2] <= sentence[2] and sentence[2] <= strongBox[-1][2] * 1.2: #if the sentence is in the vertical limits of strong box
                        newCoordinate = newCoordinate + [(strongBox[0][1],strongBox[0][2])]

            newCoordinate = sorted(newCoordinate,key=itemgetter(0),reverse=True)
            result = None
            if newCoordinate == []:
                  elementWeakTextBox = elementWeakTextBox + [sentence]  # There's not a good strong box
            else:
                  for index in newCoordinate:
                         if result == None and sentence[1] >= index[0]:
                                result = index
                         else:
                                continue
            for index in range(len(strongTextBox)):
                 if result == (strongTextBox[index][0][1],strongTextBox[index][0][2]):
                        strongTextBox[index].insert(-2,sentence) # trick to keep efficency and allows the program to work properly
                 else:
                        continue
        weakTextBox = elementWeakTextBox

        return strongTextBox, weakTextBox



def mostCommonByFont(dictLines, dictFonts):
    biggies = []
    boldies = []
    listSize = []
    for i in dictFonts:
        listSize= listSize + [(dictFonts[i]['number'],dictFonts[i]['size'])]
    mostOffenSize = max(listSize)
#    print mostOffenSize
    listOften = []
    listSelten = []
    for element in dictLines:
        if int(dictFonts[str(element[3])]['size']) >= int(mostOffenSize[1]):
            listOften += [element]
        if int(dictFonts[str(element[3])]['size']) > int(mostOffenSize[1]):
            biggies += [element]
        if dictFonts[str(element[3])]['weight'] == 'bold':
            boldies += [element]
        else:
            listSelten += [element]
    return listOften, listSelten, boldies,biggies
    

###############

def printHtml(datai):

       # Obtain a dictionary of the lines and a sorted list of the lines from the HTML file
       dictFonts,dictLines = fontsAndLines(datai)

       # Only text in the most common sizefont

       listOften, listSelten, nBoldies, nBiggies = mostCommonByFont(dictLines,dictFonts)

       # The text is organized in Textboxes
        
       textBoxes = getTextBoxes(listOften)
       
       # Divides the text boxes in weak and strong

       strongTextBox, weakTextBox = getStrongWeakBoxes(textBoxes)

       # Tries to find a strong text box for a weak group

       strongTextBox, weakTextBox = depureTextBoxes(strongTextBox, weakTextBox)
                             
       # Sorts inside strong textboxes

       for index in range(len(strongTextBox)):
              strongTextBox[index] = sorted(strongTextBox[index],key=itemgetter(2))
       
       return strongTextBox, weakTextBox, dictFonts, nBoldies, nBiggies


####


def printSource(datai):
       import urllib
       import re
       sock = urllib.urlopen(datai)
       htmlSource = sock.read()
       sock.close()

class textGenerator:
    def __init__(self,path):
        biggies, boldies, textList = createText(path)
        self.biggies = biggies  # All lines in a big font
        self.boldies = boldies  # All lines in bold
        self.textList = textList # Text as a list of lines
