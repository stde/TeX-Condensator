
# -*- coding: cp1252 -*-

#########################            

# Slides Generator

#########################

import re
from math import ceil
from tree_finder import treeFinder
from operator import itemgetter

###############

# 0 = on!

debug1 = 1

##############


### createOpening

##############


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



############################

### createOutline

############################

def createOutLine(sections):

       listTitles = []
       
       for element in sections:
              string = ''
              for twople in element:
                     string += ' ' + twople[0] + ' '
              string = ' '.join(re.split(' +',string))
              listTitles += [string]

       
       outLineString = (r'''%--- the presentation begin here -----------------%
\begin{frame}
\frametitle{Outline}
  
\begin{itemize}
''')
       for section in listTitles:
              outLineString = outLineString + (' \item %s \n' % section)

       outLineString = outLineString + (r'''\end{itemize}
\end{frame}
%%
''')
       print outLineString
       return outLineString, listTitles

############################
       

### createBody

###########################


def createBody(structure,textString,dictionary,parameter):
       body = '%%%'
       reExp = re.compile('\#\>(.+?)\<\#',re.DOTALL)
       sectionsText = re.findall(reExp,textString)
       nSectionsText = []

       # Text Cleaning!!

       for element in sectionsText:
             nSectionsText += [re.sub('&','\&',element)]
       sectionsText = nSectionsText

       # Actual Slides Writer
       
       for section in sectionsText:
              title = structure[sectionsText.index(section)] # Title
              # Calculate number of slides for a section

              rateSectionText = float(len(section)) / float(len(textString))
              slidesForSection = ceil(rateSectionText * parameter['numberOfSlides'])
              

              if debug1 == 0:
                     print slidesForSection
                     
              tree = treeFinder(section,dictionary,parameter)
              listSentences = tree.listSentences
              
              #calculate for every slide


              listSentences = sorted(listSentences,key=itemgetter(1))
              for i in range(int(slidesForSection)):
                     numberOfLetters = 0
                     nListSentences = []
                     while numberOfLetters <= parameter['charactersProSlide']:
                            try :
                                   variable = listSentences.pop()
                                   nListSentences += [variable]
                                   numberOfLetters += len(variable[0])
				   # print numberOfLetters
                            except IndexError:
                                   numberOfLetters = parameter['charactersProSlide'] + 1
				  
                     body += writeBodySlide(nListSentences,title)
              
       return body
       

####

def writeBodySlide(sentences,title):
       body = ''
       contentSlide = ''
       for sentence in sentences:   
                  contentSlide += (r'''
  \item  ''') + sentence[0]
       body += (r'''
\begin{frame}[plain]
''')

       body += ('\\frametitle{%s}' % title)
       body += (r'''
 \begin{itemize}''') + contentSlide + (r'''

 \end{itemize}

\end{frame}

%%%
''')
       return body
       

### createFile

def createFile(data,sections,textString,dictionary,parameter):
       slides = open("presentation.tex","w")
       fileString = ''
       startSlides = createOpening(data)
       outLine, listTitles = createOutLine(sections)
       bodySlides = createBody(listTitles,textString,dictionary,parameter)
       endSlides = (r'\end{document}')
       fileString = fileString + startSlides + outLine + bodySlides + endSlides
       slides.write(fileString)
       slides.close()

  #     print fileString

class writeSlides:
       def __init__(self,data,sections,textString,dictionary,parameter):
              createFile(data,sections,textString,dictionary,parameter)
