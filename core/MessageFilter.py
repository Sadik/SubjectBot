import nltk.tag, nltk.data
from nltk import wordpunct_tokenize, word_tokenize, sent_tokenize

def tokenize(text):
	sents = sent_tokenize(text)
	result = []
	for s in sents:
		words = [w.lower() for w in nltk.Text(wordpunct_tokenize(s)) if w.isalpha()]
		result.append(words)
	return result

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

		train_sents = [
		    [('ich', 'PC'), ('bin', 'PV'), ('dabei', 'None')],
		    [('ich', 'None'), ('bin', 'None'), ('nicht', 'NV'), ('dabei', 'None')],
		    [('bin', 'PV'), ('ich', 'PC'), ('dabei', 'None')],
		    [('nicht','NV'), ('schlecht', 'NV')]
		]

		self.message = message
		sent_tagger = nltk.tag.UnigramTagger(train_sents)
		self.tagger = nltk.tag.UnigramTagger(model=self.model, backoff=sent_tagger)

		evaluate(self.tagger, sentences)

	def analyze(self):
		print("analyzing text: " + self.message.text)
		print("tokens: ")
		print(tokenize(self.message.text))
		tok_sents = tokenize(self.message.text)
		
		tagger = self.tagger
		for tok_sent in tok_sents:
			tagged_sent = tagger.tag(tok_sent)
			print("tagged:")
			print(tagged_sent)




#A - Action
#P - Place
#TS - Time Specification
#PC - Participant (Name)
#C - Cost
#NV - negative value
#PV - positive Value