import nltk.tag, nltk.data
from nltk import wordpunct_tokenize, word_tokenize, sent_tokenize
import os
import pickle
from core import EventFrame

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

		#prepare different lists
		print (os.getcwd())
		self.neg_list = set([line.strip() for line in open("./lists/neg_list", "r")])
		self.pos_list = set([line.strip() for line in open("./lists/pos_list", "r")])
		self.action_list = set([line.strip() for line in open("./lists/action_list", "r")])
		self.time_expression_list = set([line.strip() for line in open("./lists/time_expression_list", "r")])
		self.human_name_list = set([line.strip() for line in open("./lists/human_name_list", "r")])
		self.location_list = set([line.strip() for line in open("./lists/location_list", "r")])
		self.message = message

		#flag. if text message contains one of these, then flag is 1
		self.HUMAN_NAME = 0
		self.TIME_EXP = 0
		self.LOCATION = 0
		self.ACTION = 0
		self.POS = 0
		self.NEG = 0

		#how it should be printed. Human name and time have to be resolved first
		self.HUMAN_NAME_str = ""
		self.TIME_EXP_str = ""
		self.LOCATION_str = ""
		self.ACTION_str = ""

	def showFlags(self):
		flag_str = ""
		if (self.HUMAN_NAME):
			flag_str += "HUMAN NAME\n"
		if (self.TIME_EXP):
			flag_str += "TIME EXP\n"
		if (self.LOCATION):
			flag_str += "LOCATION\n"
		if (self.ACTION):
			flag_str += "ACTION\n"
		if (self.POS):
			flag_str += "POS\n"
		if (self.NEG):
			flag_str += "NEG\n"

		return flag_str

	def isProbablyRelevant(self):
		words = self.message.text.lower()
		for word in words.split():
			if word in [l.lower() for l in self.time_expression_list]:
				self.TIME_EXP_str = word
				self.TIME_EXP = 1
			if word in [l.lower() for l in self.action_list]:
				self.ACTION_str = word
				self.ACTION = 1
			if word in [l.lower() for l in self.human_name_list]:
				self.HUMAN_NAME_str = word
				self.HUMAN_NAME = 1
			if word in [l.lower() for l in self.location_list]:
				self.LOCATION_str = word
				self.LOCATION = 1
			if word in [l.lower() for l in self.pos_list]:
				self.POS = 1
			if word in [l.lower() for l in self.neg_list]:
				self.NEG = 1

		if (self.HUMAN_NAME | self.TIME_EXP | self.LOCATION | self.ACTION):
			return True

		return False



	def updateOrCreateEventFrame(self, message):
		if (not os.path.isfile(str(message.chat.id)+"_frames")):
			f = open(str(message.chat.id)+"_frames", 'wb')
			f.close()

		result = "Something was done"
		print("looking for existing frames...")
		try:
			f = open(str(message.chat.id)+"_frames", "r+b") #read and write binary mode
			frame_list = pickle.loads(f.read())
			if len(frame_list) == 0: #create first frame
				print ("empty frame list. create new one?")
				first_frame = MessageFilter.createFrame(message, 0)
		except EOFError: #create first frame
			frame_list = []
			first_frame = MessageFilter.createFrame(message, 0)
			print ("empty frame list, creating new frame")
		except:
			print("unknown error in start_chat")
			raise

		return result
			
	@staticmethod
	def createFrame(message, id):
		print ("creating a frame for this message: " + message.text)
		frame = EventFrame.EventFrame(id)
		return "Frame created."

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