from nltk.stem.lancaster import LancasterStemmer
import re, os, pickle, nltk, WordNet
from nltk.corpus import wordnet as w
from nltk.stem.lancaster import LancasterStemmer
from collections import defaultdict
import dicts, math

# parameters
adj_factor = 0.6			# how strongly adjectives are weighted
adv_factor = 0.4			# how strongly adverbs are weighted
ver_factor = 0.7			# how strongly verbs are weighted
hyp_factor = 0.0			# how strongly hyponyms are added to their hypernyms
corpus_length = 2500000		# actual length: I don't know
syn_factor = 0.1			# how strongly synynoms are added to their synonyms

wnp = WordNet.WordNetParser()
    
def getwords(text):
    text = text.lower()
    for abbr in dicts.abbrs.keys():
        text = text.replace(" "+abbr.lower()," "+dicts.abbrs[abbr].lower())
    words = re.findall('[a-z]{2,}(?:(?:\-|\')[a-z]+)*', text)
    return words
    
def getrelfreqtext(all_words):
    words = {}
    sum_words = len(all_words)
    for word in all_words:
        if word in words:
            words[word] = words[word] + (1.0/sum_words)
        else:
            words[word] = 1.0/sum_words
    return words
    
def comparetextcorpus(relwordfreqtext,wordtags):
    file = open('ukcorpusrel.txt','r')
    corpus = pickle.load(file)
    file.close()
    pos = ['JJ','JJR','JJS','NN','NNS','RB','RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ']
    freqs = {}
    for word in relwordfreqtext:
        if word in wordtags and wordtags[word] in pos:
            if word in corpus:
                freqs[word] = relwordfreqtext[word] / corpus[word]
            else:
                freqs[word] = relwordfreqtext[word] / (1.0/corpus_length)
    return freqs    
                  
def getstems(dict):
    l = LancasterStemmer()
    stems = {}
    for word in dict:
        if word in dicts.irregforms:
            stems[word] = l.stem(dicts.irregforms[word])
        else:
            stems[word] = l.stem(word)
    return stems                
                                        
def morphology(dict,stems):
    stemvalues = {}
    
    for word in dict:
        if stems[word] in stemvalues:
            stemvalues[stems[word]] = stemvalues[stems[word]] + dict[word]
        else:
            stemvalues[stems[word]] = dict[word]           
    for word in dict:
        dict[word] = stemvalues[stems[word]]
    return dict

def NNStoNN(word):
    noun = word
    if word.endswith('ies'):
        noun = re.sub(r'ies$',r'y',word)
    elif word.endswith('ves'):
        noun = re.sub(r'ves$',r'fe',word)        
    elif word.endswith('es'):
        noun = re.sub(r'es$',r'',word)
    elif word.endswith('s'):
        noun = re.sub(r's$',r'',word)    
    return noun
    
def JJRtoNN(word):
    positive = word
    if word in dicts.irregforms:
        positive = dicts.irregforms[word]
    elif word.endswith('ier'):
        positive = re.sub(r'ier$',r'y',word)
    elif word.endswith('er'):
        if len(word)>4 and word[len(word)-4]==word[len(word)-3]:
            positive = word[:len(word)-3]
        else:
            positive = word[:len(word)-2]
    return positive
    
def JJStoNN(word):
    positive = word
    if word in dicts.irregforms:
        positive = dicts.irregforms[word]
    elif word.endswith('iest'):
        positive = re.sub(r'iest$',r'y',word)
    elif word.endswith('est'):
        if len(word)>5 and word[len(word)-5]==word[len(word)-4]:
            positive = word[:len(word)-4]
        else:
            positive = word[:len(word)-3]
    return positive

def RBtoNN(word):
    adjective = word
    if word.endswith('ily'):
        adjective = re.sub(r'ily',r'y',word)
    elif word.endswith('ly'):
        adjective = adjective[:len(word)-2]
    return adjective        
    
def RBRtoNN(word):
    adverb = word
    if word in dicts.irregforms:
        adverb = dicts.irregforms[word]
    elif word.endswith('ier'):
        adverb = re.sub(r'ier$',r'y',word)
    elif word.endswith('er'):
        if len(word)>4 and word[len(word)-4]==word[len(word)-3]:
            adverb = word[:len(word)-3]
        else:
            adverb = word[:len(word)-2]
    return RBtoNN(adverb)  
    
def RBStoNN(word):
    adverb = word
    if word in dicts.irregforms:
        adverb = dicts.irregforms[word]
    elif word.endswith('iest'):
        adverb = re.sub(r'iest$',r'y',word)
    elif word.endswith('est'):
        if len(word)>5 and word[len(word)-5]==word[len(word)-4]:
            adverb = word[:len(word)-4]
        else:
            adverb = word[:len(word)-3]
    return RBtoNN(adverb)   
    
def VBDtoNN(word): # past
    verb = word
    if word in dicts.irregforms:
        verb = dicts.irregforms[word]
    elif word.endswith('ed'):
        if len(word)>4 and word[len(word)-4]==word[len(word)-3]:
            verb = word[:len(word)-3]
        else:
            verb = word[:len(word)-2]
    return verb
    
def VBGtoNN(word): # gerund
    verb = word
    if word.endswith('ing'):
        if len(word)>5 and word[len(word)-5]==word[len(word)-4]:
            verb = word[:len(word)-4]
        else:
            verb = word[:len(word)-3]
    if verb.endswith('v'):
        verb = verb + 'e'    
    return verb                                     
    
def VBNtoNN(word): # past participle
    verb = word
    if word in dicts.irregforms:
        verb = dicts.irregforms[word]
    elif word.endswith('ed'):
        return VBDtoNN(verb)
    return verb
    
def VBZtoNN(word): # 3rd pers sing pres
    verb = word
    if word in dicts.irregforms:
        verb = dicts.irregforms[word]
    elif word.endswith('ies'):
        verb = re.sub(r'ies$',r'y',word)
    elif word.endswith('s'):
        verb = word[:len(word)-1]    
    return verb

def getsinglenouns(dict,tags):
    nouns = {}
    verbs = {}
    adjadv = {}
    for word in dict:
        if word not in tags:
            continue
        elif tags[word]=='NN':
            nouns[word] = word
        elif tags[word]=='NNS':
            nouns[word] = NNStoNN(word)
        elif tags[word]=='JJ':
            adjadv[word] = word
        elif tags[word]=='JJR':
            adjadv[word] = JJRtoNN(word)
        elif tags[word]=='JJS':
            adjadv[word] = JJStoNN(word)          
        elif tags[word]=='RB':
            adjadv[word] = RBtoNN(word)    
        elif tags[word]=='RBR':
            adjadv[word] = RBRtoNN(word)    
        elif tags[word]=='RBS':
            adjadv[word] = RBStoNN(word)    
        elif tags[word]=='VB' or tags[word]=='VBP':
            verbs[word] = word 
        elif tags[word]=='VBD':
            verbs[word] = VBDtoNN(word)                                                                          
        elif tags[word]=='VBG':
            verbs[word] = VBGtoNN(word)             
        elif tags[word]=='VBN':
            verbs[word] = VBNtoNN(word)             
        elif tags[word]=='VBZ':
            verbs[word] = VBZtoNN(word)             
    return (nouns,adjadv,verbs)
    
def normalize(dict):
    maximum = max(dict.values())
    minimum = min(dict.values())
    for entry in dict:
        dict[entry] = math.log(((dict[entry]-minimum)*(9/(maximum-minimum)))+1)
    return dict                          

def synonymshypernyms(morphequal):
    nouns_syns = {}
    for key in morphequal:
        nouns_syns[key] = []
        syns = wnp.do_synonyms(key)
        for syn in syns:
            if syn in morphequal:
                nouns_syns[key].append(morphequal[syn])
        
    for key in morphequal:
        for i in range(0,len(nouns_syns[key])):
            morphequal[key] = morphequal[key] + (nouns_syns[key][i]*syn_factor)
    return morphequal
    
def getposbias(words,tags):   
    for word in words:
        if word in tags:
            if tags[word].startswith('JJ'):
                words[word] = adj_factor*words[word]
            elif tags[word].startswith('RB'):
                words[word] = adv_factor*words[word]
            elif tags[word].startswith('VB'):
                words[word] = ver_factor*words[word]
    return words 

def getwordpriority(text):
    words = getwords(text)
    relwordfreqtext = getrelfreqtext(words)
    wordtags = tagger(relwordfreqtext)   
    relwordfreqcompared = comparetextcorpus(relwordfreqtext,wordtags)
    stems = getstems(relwordfreqcompared)   
    morphequal = morphology(relwordfreqcompared,stems)   
    posbias = getposbias(morphequal,wordtags)   
    synohyps = synonymshypernyms(posbias)  
    return normalize(synohyps)

def tagger(dict):
	file = open('taggerdump.txt','w')
	for key in dict:
	    file.write(key+'\n')
	file.close()
	os.system('cmd/tree-tagger-english taggerdump.txt > taggerdump2.txt')
	file = open('taggerdump2.txt','r')
	dict = {}
	for line in file.readlines():
		l = re.search(r'^([a-zA-Z]{2,})\s+([A-Z]+)\s',line)
		if l:
			dict[l.group(1)] = l.group(2)
	return dict
	
#if __name__ == '__main__':
 #  wordpriority = getwordpriority(text)        
  #  
   # items = [(v, k) for k, v in wordpriority.items()]
    #items.sort()
    #items.reverse()
    #items = [(k, v) for v, k in items]
    #count = 0
    #for k,v in items:
     #   print "%s: %1.20f" % (k,v)
