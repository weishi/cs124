#encoding: utf-8

import math
import os
import codecs
#this package is for pluralization pattern.en.pluralize("dog")
import pattern.en

from stat_parser import Parser, display_tree

class Translator:
    def __init__(self):
        self.filename='dictionary.txt'
        self.dict = {}
        self.specialWords = [u'了', u'的']
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

    def pluralize(self, sentence):
        sent_str = ''
        for w in sentence:
            sent_str += w + ' '
        sent_str = sent_str.strip()
        tree = self.parser.parse(sent_str)
        poslist = tree.pos()
        new_sent = []
        i = 0
        while i < len(poslist):
            pos = poslist[i]
            i += 1
            new_sent.append(pos[0])
            if pos[1] == 'CD' and not pos[0] in ['1', 'a', 'an', 'one']:
                while i < len(poslist):
                    nextPos = poslist[i]
                    i += 1
                    if nextPos[1] == 'NN':
                        new_sent.append(pattern.en.pluralize(nextPos[0]))
                        break
                    else:
                        new_sent.append(nextPos[0])
        return new_sent

def main():
    runner=Translator()
    runner.loadDictionary()
    f = codecs.open('dev.data.txt','r','utf-8')
    ls = [line.strip() for line in f]
    for i in ls :
        sentence = ''
        wl = runner.baseline(i)
        wl = runner.pluralize(wl)
        for w in wl:
            sentence += w+' '
        print sentence

if __name__=='__main__':
    main()
