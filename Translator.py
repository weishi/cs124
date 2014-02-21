#encoding: utf-8

import math
import os
import codecs
import pattern.en

from stat_parser import Parser, display_tree
from nltk.tree import Tree

class Translator:
    def __init__(self):
        self.filename='dictionary.txt'
        self.dict = {}
        self.specialWords = [u'了', u'的']
        self.directions = ['east', 'west', 'south', \
        'north','northeast', 'southeast', 'northwest', 'southwest']
        self.parser = Parser()
    
    def tranlate(self):
        pass

    def loadDictionary(self):
        f = codecs.open(self.filename,'r','utf-8')
        ls = [ line.strip() for line in f]
        for i in ls :
            t = i.split(':')
            cn_word = t[0]
            en_words = [w.strip() for w in t[1].split(';')]
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

    def baseline(self, sentence):
        words = sentence.split(' ')
        en_sentence = []
        for word in words:
            if word in self.specialWords:
                continue
            if word in self.dict:
                #remove measure words
                if 'mw' in self.dict[word]:
                    if len(en_sentence) > 0 and self.isNumerical(en_sentence[-1]):
                        #change one to a
                        if en_sentence[-1].lower() == 'one':
                            en_sentence[-1] = 'a'
                        continue
                en_sentence.append(self.dict[word][0])
            else:
                en_sentence.append(word)
        en_sentence.append('.')
        return en_sentence

    def parse(self, sentence):
        sent_str = ''
        for w in sentence:
            sent_str += w + ' '
        sent_str = sent_str.strip()
        tree = self.parser.parse(sent_str)
        return tree

    def pluralize(self, tree):
        if type(tree) is Tree:
            if tree.node == 'NP':
                findCD = False
                for child in tree:
                    if child.node == 'CD' and child[0] \
                    not in ['1', 'a', 'an', 'one']:
                        findCD = True
                    if findCD and child.node == 'NN':
                        child[0] = pattern.en.pluralize(child[0])
                        return
            for child in tree:
                self.pluralize(child)



    def arrangeLoctions(self, tree):
        if type(tree) is Tree:
            if tree.node == 'NAC':
                for i in range(0, len(tree)):
                    child = tree[i]
                    if i<len(tree)-1 and child.node == 'NNP' \
                    and tree[i+1][0].lower() in ['state', 'city']:
                        del tree[i+1]
                        del tree[i]
                        tree.insert(0, child)
                    if i >= len(tree)-1:
                        break
            for child in tree:
                self.arrangeLoctions(child)

    def fowardDirctionWord(self, tree):
        if type(tree) is Tree:
            if tree.node == 'NP':
                for i in range(0, len(tree)):
                    child = tree[i]
                    if child.node in ['NNP', 'NNPS'] and child[0].lower() \
                    in self.directions:
                        del tree[i]
                        child[0] = 'the '+child[0]+' of'
                        tree.insert(0, child)
                        return
            for child in tree:
                self.fowardDirctionWord(child)


def main():
    runner=Translator()
    runner.loadDictionary()
    f = codecs.open('dev.data.txt','r','utf-8')
    ls = [line.strip() for line in f]
    for i in ls :
        sentence = ''
        wl = runner.baseline(i)
        tree = runner.parse(wl)
        runner.pluralize(tree)
        runner.fowardDirctionWord(tree)
        runner.arrangeLoctions(tree)
        wl = tree.leaves()
        for w in wl:
            sentence += w+' '
        print sentence

if __name__=='__main__':
    main()
