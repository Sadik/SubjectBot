import nltk.tag, nltk.data
from nltk import wordpunct_tokenize, word_tokenize, sent_tokenize
import os
import pickle
from core import EventFrame, Helper

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
		self.message = message

		#prepare different lists
		print (os.getcwd())
		self.neg_list = set([line.strip() for line in open("./lists/neg_list", "r")])
		self.pos_list = set([line.strip() for line in open("./lists/pos_list", "r")])
		self.action_list = set([line.strip() for line in open("./lists/action_list", "r")])
		self.time_expression_list = set([line.strip() for line in open("./lists/time_expression_list", "r")])
		self.human_name_list = set([line.strip() for line in open("./lists/human_name_list", "r")])
		self.location_list = set([line.strip() for line in open("./lists/location_list", "r")])

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

	def isProbablyRelevant(self, words=None):
		if words is None:
			words = self.message.text.lower()

		for word in words.split():
			if word in [l.lower() for l in self.time_expression_list]:
				self.TIME_EXP_str = self.resolveTime(word)
				self.TIME_EXP = 1
			if word in [l.lower() for l in self.action_list]:
				self.ACTION_str = word
				self.ACTION = 1
			if word in [l.lower() for l in self.human_name_list]:
				self.HUMAN_NAME_str = self.resolveName(word)
				self.HUMAN_NAME = 1
			if word in [l.lower() for l in self.location_list]:
				self.LOCATION_str = word
				self.LOCATION = 1
			if word in [l.lower() for l in self.pos_list]:
				self.POS = 1
			if word in [l.lower() for l in self.neg_list]:
				self.NEG = 1

		if (self.TIME_EXP | self.LOCATION | self.ACTION):
			if self.NEG == 0:
				return True

		return False

	def isContextRelevant(self, n=1):
		if n == 4:
			return False

		context_text = Helper.one_text_from_message_stream(Helper.get_latest_n_messages(self.message.chat.id, self.message.from_user.id, n))

		if self.isProbablyRelevant(context_text):
			return True
		else:
			return self.isContextRelevant(n+1)

		words = self.message.text.lower()
		for word in words.split():
			if word in [l.lower() for l in self.time_expression_list]:
				self.TIME_EXP_str = self.resolveTime(word)
				self.TIME_EXP = 1
			if word in [l.lower() for l in self.action_list]:
				self.ACTION_str = word
				self.ACTION = 1
			if word in [l.lower() for l in self.human_name_list]:
				self.HUMAN_NAME_str = self.resolveName(word)
				self.HUMAN_NAME = 1
			if word in [l.lower() for l in self.location_list]:
				self.LOCATION_str = word
				self.LOCATION = 1
			if word in [l.lower() for l in self.pos_list]:
				self.POS = 1
			if word in [l.lower() for l in self.neg_list]:
				self.NEG = 1

		if (self.TIME_EXP | self.LOCATION | self.ACTION):
			if self.NEG == 0:
				return True

		return False

	def resolveTime(self, timestr):
		return timestr

	def resolveName(self, name):
		if name.lower() == "ich":
			result = "{0} {1} ({2})".format(self.message.from_user.first_name, self.message.from_user.last_name, self.message.from_user.username)
			return result
		else:
			return name

	def readFrameList(self, message):
		#read frames from file (pickle) and return list of frames

		#create file if not exist
		if (not os.path.isfile(str(message.chat.id)+"_frames")):
			f = open(str(message.chat.id)+"_frames", 'wb')
			f.close()

		frame_list = []
		print("looking for existing frames...")
		f = open(str(message.chat.id)+"_frames", "r+b") #read and write binary mode
		while 1:
			try:
				frame_list.append (pickle.load(f))
				frame_list = sum(frame_list, [])
			except EOFError:
				break
			except:
				print("unknown error in start_chat")
				raise

		f.close()
		return frame_list

	def writeFrameList(self, message, frame_list):
		#writes frame_list into file (pickle)

		if (not os.path.isfile(str(message.chat.id)+"_frames")):
			f = open(str(message.chat.id)+"_frames", 'wb')
			f.close()

		f = open(str(message.chat.id)+"_frames", "r+b") #read and write binary mode
		pickle.dump(frame_list, f)
		f.close()

	def checkFrameList(self, frame_list):
		print ("################## frame list check #####################")
		print ("type: ", type(frame_list))
		print ("len:  ", len(frame_list))
		print (frame_list)
		for frame in frame_list:
			frame.summary()

	def updateOrCreateEventFrame(self, message):
		result = "Something was done"
		frame_list = self.readFrameList(message)

		if len(frame_list) > 0:
			frameToUpdate = self.getFrameToUpdate(message, frame_list)
			if frameToUpdate is None: #is None when no suitable frame was found
				new_frame = self.createFrame(message)
				frame_list.append(new_frame)
				result = new_frame.summary()
			else:
				new_frame = self.updateFrame(frameToUpdate)
				result = new_frame.summary()
		else:
			new_frame = self.createFrame(message)
			frame_list.append(new_frame)
			result = new_frame.summary()

		self.writeFrameList(message, frame_list)

		return result
			
	def createFrame(self, message):# first message and frame id
		print ("creating a frame for this message: " + message.text)
		frame = EventFrame.EventFrame()
		frame.add_action(self.ACTION_str)
		frame.add_location (self.LOCATION_str)
		frame.add_date(self.TIME_EXP_str)
		frame.add_time(self.TIME_EXP_str)
		frame.add_participants(self.HUMAN_NAME_str)
		return frame

	def updateFrame(self, frame):
		print("I have to update this frame:")
		frame.summary()
		if frame.what is None or frame.what == "":
			frame.add_action(self.ACTION_str)
		if frame.where is None or frame.where == "":
			frame.add_location(self.LOCATION_str)
		if frame.date is None or frame.date == "":
			frame.add_date(self.TIME_EXP_str)
		if frame.time is None or frame.time == "":
			frame.add_time(self.TIME_EXP_str)
		if self.HUMAN_NAME_str:
			frame.add_participants(self.HUMAN_NAME_str)
		print ("how is it now")
		frame.summary()
		return frame

	def getFrameToUpdate(self, message, frame_list):
		index_errors_dict = {}
		for frame in frame_list:
			print ("----------------- update check ----------------")
			errors = 0
			if (frame.what is not None and frame.what != "") and self.ACTION == 1:
				if frame.what != self.ACTION_str:
					print ("error from action")
					errors += 1

			if (frame.where is not None and frame.where != "") and self.LOCATION == 1:
				if frame.where != self.LOCATION_str:
					print ("error from location")
					errors += 1

			if (frame.date is not None and frame.date != "") and self.TIME_EXP == 1:
				if frame.date != self.TIME_EXP_str:
					print ("error from time exp")
					errors += 1

			if (frame.time is not None and frame.time != "") and self.TIME_EXP == 1:
				if frame.time != self.TIME_EXP_str:
					print ("error from time exp2")
					errors += 1

			print ("----------------- errors: ", errors, " ----------------")

			if errors == 0:
				return frame

		return None #no suitable frame was found


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