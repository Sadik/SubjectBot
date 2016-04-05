import nltk.tag, nltk.data
from nltk import wordpunct_tokenize, word_tokenize, sent_tokenize, bigrams
import os
import pickle
import time
from core import EventFrame, Helper, Parser
import datetime
import string
import re

def tokenize(text):
	text = text.lower()
	sentences = sent_tokenize(text)
	sentences = [nltk.Text(wordpunct_tokenize(sent)) for sent in sentences]

	return sentences

def removeSpecialChars(word):
	chars = re.escape(string.punctuation)
	return re.sub(r'['+chars+']', '',word)

class MessageFilter:
	"""This class filters messages for relevant content, based on a custom tagger"""
	def __init__(self, message):
		self.message = message

		#prepare different lists
		#print (os.getcwd())
		self.neg_list = set([line.strip() for line in open("./lists/neg_list", "r")])
		self.positive_list = set([line.strip() for line in open("./lists/positive_list", "r")])
		self.action_list = set([line.strip() for line in open("./lists/action_list", "r")])
		self.date_expression_list = set([line.strip() for line in open("./lists/date_expression_list", "r")])
		self.human_name_list = set([line.strip() for line in open("./lists/human_name_list", "r")])
		self.location_list = set([line.strip() for line in open("./lists/location_list", "r")])

		#flag. if text message contains one of these, then flag is 1
		self.HUMAN_NAME = 0
		self.DATE_EXP = 0
		self.TIME_EXP = 0
		self.LOCATION = 0
		self.ACTION = 0
		self.POS = 0
		self.PTKNEG = 0

		#how it should be printed. Human name and time have to be resolved first
		self.HUMAN_NAME_str = ""
		self.DATE_EXP_str = ""
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
		if (self.PTKNEG):
			flag_str += "NEG\n"

		return flag_str

	def isTimeFormat(self, input):
		try:
			time.strptime(input, '%H:%M')
			return True
		except ValueError:
			return False

	def containsTimeExp(self, words=None):
		if words is None:
			words = self.message.text.lower()

		for word in words.split():
			if self.isTimeFormat(word):
				self.TIME_EXP_str = word
				return True

		bigrams_list = list(bigrams(words.split()))
		for k,v in bigrams_list:
			if k.strip().isdigit() and v.strip().lower() == "uhr":
				self.TIME_EXP_str = k
				return True
			elif k.strip().lower() == "um" and v.strip().isdigit():
				self.TIME_EXP_str = v
				return True
		return False

	def getTimeExp(self, tag_list):
		# expects tag_list [(word1, TAG2), (word2, TAG2), ... ]
		# return updated tag_list
		word_texp = None
		for (w1, t1), (w2, t2) in list(bigrams(tag_list)):
			if w1 == 'um' and t2 == "CARD":
				word_texp = w2
			elif t1 == "CARD" and w2 == "uhr":
				word_texp = w1
			self.TIME_EXP_str = word_texp

		new_tag_list = []
		for word, tag in tag_list:
			new_tag = tag
			if self.isTimeFormat(word) or word == word_texp:
				self.TIME_EXP_str = word
				new_tag = "TEXP" # Time Expression

			new_tag_list.append((word, new_tag))

		return new_tag_list

	def NER(self, words=None):
		# gets a sentence (or a few words)
		# calls the Parser
		# returns updated pos_tag_list
		if words is None:
			words = self.message.text.lower()

		parser = Parser.Parser(words)
		pos_list = parser.pos
		#print(pos_list)
		pos_list = self.getTimeExp(pos_list)

		tag_list = []
		for word, tag in pos_list:
			new_tag = tag
			if word in [l.lower() for l in self.date_expression_list]:
				self.DATE_EXP_str = self.resolveDate(word)
				new_tag = "DEXP" # Date Expression
			elif word in [l.lower() for l in self.action_list]:
				self.ACTION_str = word
				new_tag = "ACTION"
			elif(word == "ich"):
				self.HUMAN_NAME_str = self.resolveName(word)
				new_tag = "HN" # Human Name
			elif word in [l.lower() for l in self.location_list]:
				self.LOCATION_str = word
				new_tag = "LOC"

			tag_list.append((word, new_tag))

		return tag_list



	def NER2(self, words=None):

		if words is None:
			words = self.message.text.lower()

		if self.containsTimeExp(words):
			self.TIME_EXP = 1
		for word in words.split():
			word = removeSpecialChars(word)
			if word in [l.lower() for l in self.date_expression_list]:
				self.DATE_EXP_str = self.resolveDate(word)
				self.DATE_EXP = 1
			if word in [l.lower() for l in self.action_list]:
				self.ACTION_str = word
				self.ACTION = 1
			if word in [l.lower() for l in self.human_name_list]:
				self.HUMAN_NAME_str = self.resolveName(word)
				self.HUMAN_NAME = 1
			if word in [l.lower() for l in self.location_list]:
				self.LOCATION_str = word
				self.LOCATION = 1
			if word in [l.lower() for l in self.positive_list]:
				self.POS = 1
			if word in [l.lower() for l in self.neg_list]:
				#print ("i know its negative!!!")
				self.PTKNEG = 1

	def isProbablyRelevant2(self, pos_list):
		# should only be called after NER() was called
		# expects tag_list [(word1, TAG2), (word2, TAG2), ... ]
		# return 0 for not relevant
		# 1 for contextual relevant#
		# 2 for relevant
		words = [e[0] for e in pos_list]
		tags = [e[1] for e in pos_list]
		if "ACTION" in tags and "HN" in tags:
			return 2
		if "DEXP" in tags or "TEXP" in tags:
			return 1
		if "LOC" in tags:
			return 1
		if "HN" in tags and "PTKNEG" in tags:
			return 1

		return 0


	def isProbablyRelevant(self, words=None):
		# should only be called after NER() was called
		# return 0 for not relevant
		# 1 for contextual relevant#
		# 2 for relevant
		if (self.ACTION + self.HUMAN_NAME > 1):
			return 2
		if (self.DATE_EXP + self.TIME_EXP >= 1):
			return 1
		if self.LOCATION == 1:
			return 1
		#if (self.HUMAN_NAME + self.PAV > 1):
		#	return 1
		if (self.HUMAN_NAME + self.PTKNEG + self.POS > 1):
			return 1

		return 0

	def isContextRelevant(self, n=1):
		# should only be called after isProbablyRelevant() was called
		if n == 6: #searching to a maximum of n-1
			return False

		context_text = Helper.one_text_from_message_stream(Helper.get_latest_n_messages(self.message.chat.id, self.message.from_user.id, n))
		print ("testing context relevance of :", context_text)

		self.NER(context_text)
		if self.isProbablyRelevant(context_text) == 2:
			return True
		else:
			return self.isContextRelevant(n+1)

	def resolveTime(self, timestr):
		return timestr

	def resolveDate(self, datestr):
		print ("resolving date ", datestr)
		today = time.strftime("%A").lower()
		week_list = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"]
		if (today == "saturday"):
			today = "samstag"
		elif today == "sunday":
			today = "sonntag"
		elif today == "monday":
			today = "montag"
		elif today == "tuesday":
			today = "dienstag"
		elif today == "wednesday":
			today = "mittwoch"
		elif today == "thursday":
			today = "donnerstag"
		elif today == "friday":
			today = "freitag"

		if datestr.lower() == "morgen":
			tomorrow_date = datetime.datetime.today() + datetime.timedelta(days=1)
			tomorrow_week_day = week_list[((week_list.index(today)+1) % 7)]
			return "{0}, {1}.{2}".format(tomorrow_week_day, tomorrow_date.day, tomorrow_date.month)

		if datestr.lower() in week_list:
			try:
				today_idx = week_list.index(today)
				date_idx = week_list.index(datestr)
			except ValueError:
				print ("ValueError in resolveDate for ", datestr)
				return datestr

			offset = (date_idx - today_idx) % 7
			then_date = datetime.datetime.today() + datetime.timedelta(days=offset)
			return "{0}, {1}.{2}".format(week_list[date_idx], then_date.day, then_date.month)

		return datestr

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
			except UnicodeDecodeError:
				print("UnicodeDecodeError!")
				print ("[WARNING]")
				print (EventFrame.EventFrame.readable_frame_list(frame_list))
				print ("[END OF WARNING]")
				return ("Warnung: Die Operation war nicht erfolgreich.")
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
		else:
			f = open(str(message.chat.id)+"_frames", 'w+') #TODO: deleting the file is only workaround to avoid pickle error
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

	def updateOrCreateEventFrame(self, message, tags):
		result = "verstehe ... nicht"
		frame_list = self.readFrameList(message)

		if len(frame_list) > 0: #frames already exist
			frameToUpdate = self.getFrameToUpdate(tags, frame_list)
			if frameToUpdate is None: #is None when no suitable frame was found
				new_frame = self.createFrame(message)
				if new_frame is not None:
					frame_list.append(new_frame)
					result = new_frame.summary()
			else: # found a frame that is intended to be updated
				new_frame = self.updateFrame(frameToUpdate)
				if new_frame is not None:
					result = new_frame.summary()
				else: #None: frame was deleted, probably no participants anymore
					result = "alter Vorschlag gelöscht, da keine Teilnehmer"
					#remove frameToUpdate from frame_list

					print ("I actually have to remove this frame....")
					frame_list.remove(frameToUpdate)
					print("frame list länge: ", len(frame_list))
		else: #no frame exist, create new one
			new_frame = self.createFrame(message)
			if new_frame is not None:
				frame_list.append(new_frame)
				result = new_frame.summary()

		self.writeFrameList(message, frame_list)

		return result
			
	def createFrame(self, message):# first message and frame id
		print ("creating a frame for this message: " + message.text)
		if self.PTKNEG > 0:
			return None
		frame = EventFrame.EventFrame()
		frame.add_action(self.ACTION_str)
		frame.add_location (self.LOCATION_str)
		frame.add_date(self.DATE_EXP_str)
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
			frame.add_date(self.DATE_EXP_str)
		if frame.time is None or frame.time == "":
			frame.add_time(self.TIME_EXP_str)
		if self.HUMAN_NAME_str and self.PTKNEG == 0:
			frame.add_participants(self.HUMAN_NAME_str)
		elif self.HUMAN_NAME_str and self.PTKNEG == 1:
			frame.remove_participants(self.HUMAN_NAME_str)
		print ("frame updated:")
		frame.summary()
		if len(frame.participants) == 0:
			return None

		#print ("there are participants: ", frame.participants , " (", len(frame.participants) , ")")
		return frame

	def getFrameToUpdate(self, tags, frame_list):
		# expects list of tags, list of frames
		index_errors_dict = {}
		for frame in frame_list:
			print ("----------------- update check ----------------")
			offset = 0
			print("tags:", tags)
			print("frame.what:" , frame.what)
			print(frame.what is not None)
			print(frame.what != "")
			print("ACTION" in tags)
			if (frame.what is not None and frame.what != "") and "ACTION" in tags:
				print("1. check true")
				if frame.what != self.ACTION_str:
					print ("offset from action")
					offset += 1
			else:
				print ("1. check false")
			if (frame.where is not None and frame.where != "") and "LOC" in tags:
				if frame.where != self.LOCATION_str:
					print ("offset from location")
					offset += 1

			if (frame.date is not None and frame.date != "") and "DEXP" in tags:
				if frame.date != self.DATE_EXP_str:
					print ("offset from date exp")
					offset += 1

			if (frame.time is not None and frame.time != "") and "TEXP" in tags:
				if frame.time != self.TIME_EXP_str:
					print ("offset from time exp")
					offset += 1

			print ("----------------- offset: ", offset, " ----------------")

			if offset == 0:
				return frame

		return None #no suitable frame was found


	def analyze(self):
		tok_sents = tokenize(self.message.text)
		sentence_values = self.analyze_pos_neg(tok_sents)

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

		pn_tagged_sents = [None] * len(tok_sents)
		i = 0
		for sent in tok_sents:
			sentence_value = "PV"
			if self.neg_list.intersection(sent):
				sentence_value = "NV"
			pn_tagged_sents[i] = sentence_value
			i = i+1
		return pn_tagged_sents






#A - Action
#P - Place
#TS - Time Specification
#PC - Participant (Name)
#C - Cost
#NV - negative value
#PV - positive Value