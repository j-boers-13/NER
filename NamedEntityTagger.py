import nltk
import sys
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import Counter
from nltk.tag.stanford import NERTagger
import os
import itertools
import wikipedia
reload(sys)
sys.setdefaultencoding('utf-8')

def standfordtagger(words):
	try: 
		os.environ['JAVAHOME'] = ''
		path = ""
		classifier = path + ""
		jar = path + "/stanford-ner-3.4.jar" 
		
		st = NERTagger(classifier, jar)
		stanford_tagger = st.tag(words)
		return stanford_tagger
	except: print(words)
			
def wordnet_tagger(x):
	classes = ["animal", "country", "natural place", "sport", "entertainment", "city"]
	if x == "," or x == "." or x == "'" or x == '"' or x == "\n" or x == "?" or x == "!":
		return []
	else:
		try:
			lemma = x + '.n.01'
			word = wordnet.synset(lemma)
			hyper = lambda s: s.hypernyms()
			hyperlist = list(word.closure(hyper))
			for hyper in hyperlist:
				hyper = str(hyper)
				for cls in classes:
					if cls in hyper:
						return cls.upper()[:3]
		except(nltk.corpus.reader.wordnet.WordNetError):
			return False

def links(d,entity_tags3,words):
	if entity_tags3[d-2] != "O" and entity_tags3[d] != "O" and entity_tags3[d-2] == entity_tags3[d]:
		wikilinks = wikify(words[d-2] + "_" + words[d-1] + "_" + words[d])
		return wikilinks
	elif entity_tags3[d] != "O" and entity_tags3[d+1] != "O" and entity_tags3[d-1] == entity_tags3[d+1]:
		wikilinks = wikify(words[d-1] + "_" + words[d] + "_" + words[d+1])
		return wikilinks
	elif entity_tags3[d] != "O" and entity_tags3[d] == entity_tags3[d-1]:
		wikilinks = wikify(words[d-1] + "_" + words[d])
		return wikilinks
	elif entity_tags3[d-3] != "O" and entity_tags3[d-2] != "O" and entity_tags3[d-3] == entity_tags3[d-1]:
		wikilinks = wikify(words[d-3] + "_" + words[d-2] + "_" + words[d-1])
		return wikilinks
	elif entity_tags3[d-2] != "O" and entity_tags3[d-2] == entity_tags3[d-1]:
		wikilinks = wikify(words[d-2] + "_" + words[d-1])
		return wikilinks
	else:
		wikilinks = wikify(words[d-1])
		return wikilinks

def wikify(i):
	links = wikipedia.page(wikipedia.search(i)[0]).url
	return links
	
	
def loctags(word):
	loctags = ["country","state","city","capital"]
	wikilinks = wikipedia.page(wikipedia.search(word)[0])
	for loc in loctags:
		if (loc in wikilinks.content[:300]):
			if loc == "city" or loc == "capital":
				return ("CIT")
			elif loc == "country" or loc == "state":
				return ("COU")
	return ("COU")
	
def main(argv):

	words = []
	f = open("development.set")
	lines=[]
	for line in f:
		lines.append(line.strip())
		line = line[:-1]
		wordsline = line.split(" ")
		x=0
		for word in wordsline:
			if word != "" and word != "-" and word != " ":
				x = x+1
				if x%5 == 0:
					words.append(word.decode('utf-8'))
	entity_tags = standfordtagger(words)
	entity_tags2 = sum(entity_tags, [])
	entity_tags3 = []
	for x,y in entity_tags2:
		entity_tags3.append(y)
	g = open("development5.ent", 'w+')
	d=0
	tag=0
	for line in lines:
		line = line.split()[:6]
		linestr = ' '.join(str(e) for e in line)
		if len(line) > 3:
			d=d+1
			try:
				if entity_tags3[d-1] == "O":
					tag = wordnet_tagger(words[d-1])
					if tag:
						entity_tags3[d-1] = tag
						link = links(d,entity_tags3,words)
						print(words[d-1],entity_tags3[d-1])
					else:
						g.write(linestr + "\n")
				elif entity_tags3[d-1] == "LOCATION":
					link = links(d,entity_tags3,words)
					g.write(linestr + " " + loctags(words[d-1]) + " " + link + "\n")
					
				else:
					link = links(d,entity_tags3,words)
				if entity_tags3[d-1] != "O" and entity_tags3[d-1] != "LOCATION":
					g.write(linestr + " " +  entity_tags3[d-1][:3] + " " + link + "\n")
			except(wikipedia.exceptions.DisambiguationError):
				try:
					disambig = str(sys.exc_info()[1]).split("\n")
					if tag:
							link = wikify(disambig[1])
					elif entity_tags3[d-1] == "LOCATION":
						link = links(d,entity_tags3,words)
						g.write(linestr + " " + loctags(disambig[1]) + " " + link + "\n")
					else:
						words[d-1] = disambig[1]
						link = links(d,entity_tags3,words)
					if entity_tags3[d-1] != "O" and entity_tags3[d-1] != "LOCATION":
						g.write(linestr + " " + entity_tags3[d-1][:3] + " " + link + "\n")
				except(wikipedia.exceptions.DisambiguationError):
					disambig = str(sys.exc_info()[1]).split("\n")
					print('exception', words[d-1])
					if entity_tags3[d-1] == "LOCATION" and words[d-1] != "independent":
						print(disambig[2])
						link = wikify(disambig[2])
						g.write(linestr + " " + loctags(disambig[2]) + " " + link + "\n")
					else:
						g.write(linestr + " " + entity_tags3[d-1][:3] + "\n")
						
				except(IndexError):
					g.write(linestr + " " + entity_tags3[d-1][:3] + "\n")
			except(IndexError):
				g.write(linestr + " " + entity_tags3[d-1][:3] + "\n")
			except(wikipedia.exceptions.PageError):
				if entity_tags3[d-1] == "LOCATION":
					g.write(linestr + " " + "COU" + "\n")
				else:
					g.write(linestr + " " + entity_tags3[d-1][:3] + "\n")
		else:
			g.write(linestr + "\n")
				
				
				
				
				


		
if __name__ == "__main__":
	main(sys.argv)
