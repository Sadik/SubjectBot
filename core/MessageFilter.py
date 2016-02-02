import nltk.tag, nltk.data
from nltk import wordpunct_tokenize, word_tokenize, sent_tokenize
import os

def tokenize(text):
	text = text.lower()
	sentences = sent_tokenize(text)
	sentences = [nltk.Text(wordpunct_tokenize(sent)) for sent in sentences]

	return sentences

def evaluate(tagger, sentences):
    good,total = 0,0.
    for sentence,func in sentences:
        tags = tagger.tag(nltk.word_tokenize(sentence))
        print ("tags")
        print (tags)
        good += func(tags)
        total += 1
    print ('Accuracy:',good/total)

class MessageFilter:
	"""This class filters messages for relevant content, based on a custom tagger"""
	def __init__(self, message):

		print (os.getcwd())
		self.neg_list = set([line.strip() for line in open("./lists/neg_list", "r")])
		self.pos_list = set([line.strip() for line in open("./lists/pos_list", "r")])
		self.action_list = set([line.strip() for line in open("./lists/action_list", "r")])
		self.time_expression_list = set([line.strip() for line in open("./lists/time_expression_list", "r")])
		self.human_name_list = set([line.strip() for line in open("./lists/human_name_list", "r")])
		self.message = message

	def isProbablyRelevant(self):
		words = self.message.text.lower()
		for word in words.split():
			list_words = [l.lower() for l in self.time_expression_list | self.action_list | self.time_expression_list | self.human_name_list]
			if word in list_words:
				return True

		return False

	def analyze(self):
		tok_sents = tokenize(self.message.text)
		sentence_values = self.analyze_pos_neg(tok_sents)
		print ("sentence values")
		print (sentence_values)

		tagger = self.tagger
		resulting_str = ""
		for tok_sent in tok_sents:
			tagged_sent = tagger.tag(tok_sent)
			resulting_str += str(tagged_sent)

		return resulting_str

	def analyze_pos_neg(self, tok_sents):
		""""tokenized sentences. [[s0w0, s0w1,...],[s1w0, s1w1],...,[snw0,snw1,...]]
		s: sentence
		w: word """
		print ("tokenized sentences:")
		print (tok_sents)

		pn_tagged_sents = [None] * len(tok_sents)
		i = 0
		for sent in tok_sents:
			print (sent)
			sentence_value = "PV"
			if self.neg_list.intersection(sent):
				sentence_value = "NV"
			pn_tagged_sents[i] = sentence_value
			i = i+1
		return pn_tagged_sents

	def analyze_message_stream(self, message_stream):
		print ("############ Messages in Stream ############")
		for message in message_stream:
			print (message)




#A - Action
#P - Place
#TS - Time Specification
#PC - Participant (Name)
#C - Cost
#NV - negative value
#PV - positive Value