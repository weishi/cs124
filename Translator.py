#encoding: utf-8

import math
import os
import re
import collections
import codecs
import pattern.en
from pattern.en import verbs, conjugate, PARTICIPLE
import nltk
import nltk.collocations
import nltk.corpus

from stat_parser import Parser, display_tree
from nltk.tree import Tree
from pattern.en import conjugate

class Translator:
    def __init__(self):
        self.filename='dictionary.txt'
        self.dict = {}
        bgm  = nltk.collocations.BigramAssocMeasures()
        finder = nltk.collocations.BigramCollocationFinder.from_words(nltk.corpus.brown.words())
        scores = finder.score_ngrams(bgm.likelihood_ratio)
        self.scored = {}
        for key, score in scores:
            self.scored[key] = score
        self.specialWords = [u'了', u'的']
        self.directions = ['east', 'west', 'south', \
        'north','northeast', 'southeast', 'northwest', 'southwest']
        self.parser = Parser()
    
    def tranlate(self):
        pass

    def loadDictionary(self):
        f = codecs.open(self.filename,'r','utf-8')
        regex = re.compile('(.*)\((.*)\)')
        ls = [ line.strip() for line in f]
        for i in ls :
            t = i.split(':')
            cn_word = t[0]
            en_words = []
            for w in t[1].split(';'):
                word = w.strip()
                m = regex.match(word) 
                if (m is not None):
                    en_words.append((m.group(1).strip(), m.group(2).strip()))
                else:
                    en_words.append((w.strip(), 'default'))
            self.dict[cn_word] = en_words
        f.close()

    def isNumerical(self, word):
        if word.isdigit():
            return True
        word = word.lower()
        if word in ['one', 'a', 'an']:
            return True
        else:
            return False

    def preProcess(self, sentence, pickWord):
        words = sentence.split(' ')
        en_sentence = []
        for word in words:
            w = word.split('#')
            word = w[0]
            t = w[1]
            if word == u'。':
                word = '.'
            elif word == u'，':
                word = ','
            elif word == u'“' or word == u'”':
                word = '"'
            elif word == u'、':
                word = ','
            elif word == u'：':
                word = ':'
            elif word == u'``':
                word = '"'
            if word in self.specialWords:
                #add tense
                if word == u'了':
                    en_sentence[-1] = conjugate(en_sentence[-1].strip(), 'p')
                continue
            if word in self.dict:
                #remove measure words
                if 'M' == type:
                    if len(en_sentence) > 0 and self.isNumerical(en_sentence[-1]):
                        #change one to a
                        if en_sentence[-1].lower() == 'one':
                            en_sentence[-1] = 'a'
                    continue
                if pickWord == 'baseline':
                    en_sentence.append(self.dict[word][0][0])
                else:
                    if len(en_sentence) > 0:
                        en_sentence.append(self.pick(self.dict[word], t, en_sentence[-1]))
                    else:
                        en_sentence.append(self.pick(self.dict[word], t, ''))
            else:
                en_sentence.append(word)
        return en_sentence

    def pick(self, dict, t, prev):
        candidates = []
        for w in dict:
            if w[1] == t:
                candidates.append(w[0])
        if len(candidates) == 0:
            for w in dict:
                candidates.append(w[0])
        if prev == '':
            return candidates[0]
        else:
            return max(candidates, key=lambda x:self.scored[(prev, x)] if (prev, x) in self.scored else 0)

    def parse(self, sentence):
        sent_str = ''
        for w in sentence:
            sent_str += w + ' '
        sent_str = sent_str.strip()
        tree = self.parser.parse(sent_str)
        return tree

    def orderOneOf(self, sentence):
        full_sentence = nltk.word_tokenize(' '.join(sentence))
        tags = nltk.pos_tag(full_sentence)
        new_sentence = []
        for i in range(len(full_sentence) - 1):
            if full_sentence[i] == 'one' and full_sentence[i + 1] == 'of':
                for j in reversed(range(i - 1)):
                    if 'VB' in tags[j][1] and tags[j][1] != 'VBD' and tags[j + 1][1] == 'RB':
                        new_sentence.insert(j + 2, 'of')
                        new_sentence.insert(j + 2, 'one')
                        break
                    elif tags[j][1] == 'IN' or ('VB' in tags[j][1] and tags[j][1] != 'VBD'):
                        new_sentence.insert(j + 1, 'of')
                        new_sentence.insert(j + 1, 'one')
                        break
            elif i < 2 or (full_sentence[i] != 'of' and full_sentence[i - 1] != 'one'):
                new_sentence.append(full_sentence[i])
        return new_sentence

    def pluralize(self, tree):
        if type(tree) is Tree:
            if tree.node in ['VB', 'VP'] and not type(tree[0]) is Tree:
                tree[0] = pattern.en.conjugate(tree[0], '3sg')
            #if tree.node == 'VBP':
            #   tree[0] = pattern.en.conjugate(tree[0], tense=PARTICIPLE, parse=True)
            if tree.node in ['NP','ADJP','UCP']:
                findCD = False
                for child in tree:
                    if child.node == 'CD' and not type(child[0]) is Tree\
                    and child[0].lower() not in ['1', 'a', 'an', 'one']:
                        print "aaa"
                        findCD = True
                    if child.node == 'JJ' and not type(child[0]) is Tree\
                    and child[0].lower() in ['many', 'numerous', 'a lot']:
                        print "bb"
                        findCD = True
                    if child.node == 'QP':
                        print "cc"
                        findCD = True
                    if findCD and child.node == 'NN':
                        child[0] = pattern.en.pluralize(child[0])

            for child in tree:
                self.pluralize(child)

    def arrangeLocations(self, tree):
        if type(tree) is Tree:
            if tree.node == 'NAC':
                for i in range(0, len(tree)):
                    child = tree[i]
                    if i<len(tree)-1 and child.node == 'NNP' \
                    and not type(tree[i+1][0]) is Tree and \
                    tree[i+1][0].lower() in ['state', 'city']:
                        del tree[i+1]
                        del tree[i]
                        tree.insert(0, child)
                    if i >= len(tree)-1:
                        break
            for child in tree:
                self.arrangeLocations(child)

    def forwardDirectionWord(self, tree):
        if type(tree) is Tree:
            if tree.node == 'NP':
                for i in range(0, len(tree)):
                    child = tree[i]
                    if child.node in ['NNP', 'NNPS'] and \
                    not type(child[0]) is Tree and child[0].lower() \
                    in self.directions:
                        del tree[i]
                        child[0] = 'the '+child[0]+' of'
                        tree.insert(0, child)
                        return
            for child in tree:
                self.forwardDirectionWord(child)

    def suchAs(self,sentence):
        st=' '.join(sentence)
        reg=r'for example : ([\w\s,]+) etc\.'
        st=re.sub(reg, 'such as \g<1>, etc', st)
        return st.split(' ')


    def arrangeDate(self,sentence):
        year=r'[12]\d{3}'
        month=r'January|February|March|April|May|June|July|August|September|October|November|December' 
        day=r'\d{1,2}'
        for i in range(len(sentence)):
            yWord=mWord=dWord=''
            word=sentence[i]
            if re.match(year,word):
                yWord=sentence[i]
                if i+1<len(sentence):
                    nextWord=sentence[i+1]
                    if re.match(month, nextWord):
                        mWord=nextWord.capitalize()
                        if i+2<len(sentence):
                            nextNextWord=sentence[i+2]
                            if re.match(day, nextNextWord):
                                dWord=nextNextWord
            if yWord!='' and mWord!='' and dWord!='':
                sentence[i:i+3]=[mWord, dWord, yWord]
                i+=3
            elif yWord!='' and mWord!='':
                sentence[i:i+2]=[mWord, yWord]
                i+=2

        return sentence

    def superlative(self, tree):
        if type(tree) is Tree:
            for i in range(0, len(tree)):
                if i+1<len(tree):
                    if tree[i].node=='RBS' and tree[i+1].node=='JJ':
                        if type(tree[i][0]) is not Tree and \
                        type(tree[i+1][0]) is not Tree:
                            superWord = 'the ' + pattern.en.superlative(tree[i+1][0])
                            if 'most'==superWord:
                                del tree[i+1]
                            elif 'most' not in superWord:
                                tree[i+1][0]=superWord
                                del tree[i]
                        return
            for child in tree:
                self.superlative(child)


    def postProcess(self,sentence):
        strategies=[\
        (self.pluralize, True), \
        (self.forwardDirectionWord, True), \
        (self.arrangeLocations, True),\
        (self.superlative, True),\
        (self.arrangeDate, False),\
        (self.orderOneOf, False), \
        (self.suchAs, False)\
        ]

        #Process flat sentence first
        for (func,isTree) in strategies:
            if not isTree:
                sentence=func(sentence)

        #Process sentence tree 
        tree=self.parse(sentence)
        for (func,isTree) in strategies:
            if isTree:
                func(tree)

        wl=tree.leaves()
        result=''
        for i in range(len(wl)):
            if i==0:
                result=wl[0].capitalize()
            elif wl[i]==',' or wl[i]=='.':
                result+=wl[i]
            else:
                result+=' '+wl[i]
        return result+'.' 




def main():
    runner=Translator()
    runner.loadDictionary()
    
    f = codecs.open('dev.data.pos.txt','r','utf-8')
    ls = [line.strip() for line in f]
    for i in ls :
        sentence = ''
        wl = runner.preProcess(i, 'baseline')
        print 'Base  =>', ' '.join(wl) 
        #tree = runner.parse(wl)
        #display_tree(tree)
        wl = runner.preProcess(i, 'advanced')
        sentence=runner.postProcess(wl)
        #wl = tree.leaves()
        #for w in wl:
        #    sentence += w+' '
        print 'After =>', sentence 

if __name__=='__main__':
    main()
