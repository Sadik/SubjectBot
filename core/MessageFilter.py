import nltk.tag, nltk.data
from nltk import wordpunct_tokenize, word_tokenize, sent_tokenize

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
		self.model = {
		'fußball': 'A',
		'fussball':'A',
		'handball':'A',
		'joggen':'A',
		'bolzen':'A',
		'montag':'TS',
		'dienstag':'TS',
		'mittwoch':'TS',
		'donnerstag':'TS',
		'freitag':'TS',
		'samstag':'TS',
		'sonntag':'TS',
		'nein':'NV',
		'nicht': 'NV',
		'schlecht': 'NV',
		'ja':'PV',
		'gut': 'PV'
		}
		
		sentences = [
		    ('ich bin dabei', lambda tags: ('ich', 'PC') in tags),
		    ('ich bin nicht dabei', lambda tags: ('nicht', 'NV') in tags),
		    ('bin ich dabei', lambda tags: ('ich', 'PC') in tags),
		    ('nicht schlecht', lambda tags: ('nicht', 'PV') in tags),
		    ('fußball spielen', lambda tags: ('fußball', 'A') in tags)
		]

		traindata = [
			[('ich bin dabei', 'PV')],
		    [('ich', 'test'), ('bin', 'None'), ('nicht', 'NV'), ('dabei', 'None')]
		]

		self.message = message
		#sent_tagger = nltk.tag.UnigramTagger(model=self.model)
		#self.tagger = nltk.tag.TrigramTagger(traindata, backoff=sent_tagger)

		t0 = nltk.DefaultTagger('None')
		t1 = nltk.UnigramTagger(model=self.model, backoff=t0)
		t2 = nltk.BigramTagger(traindata, backoff=t1)
		t3 = nltk.TrigramTagger(traindata, backoff=t2)

		self.tagger = t3

		#evaluate(self.tagger, sentences)

	def analyze(self):
		#print("analyzing text: " + self.message.text)
		tok_sents = tokenize(self.message.text)
		tagger = self.tagger
		resulting_str = ""
		for tok_sent in tok_sents:
			#print ("trying to tag: ")
			#print (tok_sent)
			tagged_sent = tagger.tag(tok_sent)
			#print("tagged:")
			#print(tagged_sent)
			resulting_str += str(tagged_sent)

		return resulting_str

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