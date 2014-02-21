#encoding: utf-8
import math
import os
import codecs

class Translator:
	def __init__(self):
		self.filename='dictionary.txt'
		self.dict = {}
		self.specialWords = [u'了', u'的']
	
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

	def baseline(self, sentence):
		words = sentence.split(' ')
		en_sentence = ''
		for word in words:
			if word in self.specialWords:
				continue
			if word in self.dict:
				en_sentence += ' '+self.dict[word][0]
			else:
				en_sentence += ' '+word
		en_sentence = en_sentence.strip() + '.'
		return en_sentence

def main():
	runner=Translator()
	runner.loadDictionary()
	f = codecs.open('dev.data.txt','r','utf-8')
	ls = [line.strip() for line in f]
	for i in ls :
		print runner.baseline(i)

if __name__=='__main__':
	main()
