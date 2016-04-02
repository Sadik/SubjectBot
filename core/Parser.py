import re, string
import subprocess
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tree import Tree
from tempfile import NamedTemporaryFile

# from core import Parser
# tree = Parser.parse_one_sentence("Dies ist nur ein Test")

def parse_one_sentence(sentence):
	# starts parser for one sentence and returns a list of tuples (word, tag)
	# Stuttgart/Tübinger Tagsets
	fp = NamedTemporaryFile('w+')
	fp.write(sentence.lower())
	print ("fp.name: ", fp.name)
	fp.seek(0)
	rc = subprocess.call(
		["./thirdparty/stanford-parser-full-2015-12-09/lexparser-lang.sh", "German", "500", 
		"edu/stanford/nlp/models/lexparser/germanFactored.ser.gz", 
		"output", str(fp.name)])
	filename = fp.name + ".output"
	fp.close()

	tree_string = open(filename,'r').read()
	print (tree_string)
	tree = Tree.fromstring(tree_string)
	return tree
	return tree.pos()

def removeSpecialChars(word):
	chars = re.escape(string.punctuation)
	return re.sub(r'['+chars+']', '',word)

class Parser:
	"""Parser stuff."""
	def __init__(self, text):
		self.text = text.lower()
		self.sentence_list = sent_tokenize(text)
		self.start_parsing()

	def sentence_tokenize(self, text):
		return sent_tokenize(text)

	def word_tokenize(self, text):
		return word_tokenize(removeSpecialChars(text))

	def start_parsing(self):
		rc = subprocess.call(
		["./lexparser-lang.sh", "German", "500", 
		"edu/stanford/nlp/models/lexparser/germanFactored.ser.gz", 
		"output", file])
	def tag_text(self, text):
		
		return text

