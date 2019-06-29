from collections import Counter
from nltk.metrics import ConfusionMatrix
import nltk
import sys
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import Counter
reload(sys)
sys.setdefaultencoding('utf-8')

def ifTag(wordsline,tags):
	for word in wordsline:
		for tag in tags:
			if tag in word:
				# use 'return http' for measurement of the same link spaces, use 'return tag' for the measurement of Entities and use the other part for the measurement of the links that were exactly the same
				#return http
				#return tag
				if 'https' in word:
					word = "http://en" + word[10:]
					return word
				else:
					if 'http' in word:
						word = "http://en" + word[9:]
						return word

def main(argv):
	
	listFile1 = []
	listFile2 = []
	
	#choose whichs tags you want the program to use
	tags = ['https', 'http'] 
	#tags = ['COU', 'NAT', 'ENT', 'SPO', 'ANI', 'ORG', 'CIT', 'PER']	
	
	f = open("test.set.ent")
	lines=[]
	for line in f:
		tag = 0
		lines.append(line.strip())
		line = line[:-1]
		wordsline = line.rstrip("\r").split()
		tagged = ifTag(wordsline,tags)
		if tagged:
			listFile1.append(tagged)
		else:
			listFile1.append('x')
	print(listFile1)
	g = open("test.set")
	for line in g:
		tag = 0
		lines.append(line.strip())
		line = line[:-1]
		wordsline = line.rstrip("\r").split()
		tagged = ifTag(wordsline,tags)
		if tagged:
			listFile2.append(tagged)
		else:
			listFile2.append('x')
	#print(listFile2)
	#measurement factor for the amount of links that are the same for both lists	
	TP = 0
	TN = 0
	FP = 0
	FN = 0
	c = 0
	d = 0
	Hoi = 0
	TOTAL=0
	goldstandard=0
	onze=0
	
	for link in listFile1:
		c = c + 1
		if link != "x":
			goldstandard += 1
		if listFile2[c-1] != "x":
			onze += 1
		if link == listFile2[c-1] and link != "x":
			TP += 1
		if listFile2[c-1] != "x" and link == "x":
			FN += 1
		if link == "x" and listFile2[c-1] == "x":
			TN += 1
		if link != "x" and listFile2[c-1] == "x":
			FP += 1
		if link != "x" and listFile2[c-1] != "x" and listFile2[c-1] != link: 
			Hoi += 1
		
	print(goldstandard,"gs")
	print(onze,"ons")
	print("TP",TP)
	print("FP",FP)
	print("TN",TN)
	print("FN",FN)
	print("hoi", Hoi)
	#--------------------------------------------------------------------------
	
	cm = ConfusionMatrix(listFile1, listFile2)
	print(cm)
	
	# choose which labels u want to be used by the program
	labels = set("http x".split())
	#labels = set("COU NAT ENT SPO ANI ORG CIT PER x".split())
	
	true_positives = Counter()
	false_negatives = Counter()
	false_positives = Counter()

	for i in labels:
		for j in labels:
			if i == j:
				true_positives[i] += cm[i,j]
			else:
				false_negatives[i] += cm[i,j]
				false_positives[j] += cm[i,j]

	print("TP:", sum(true_positives.values()), true_positives)
	print("FN:", sum(false_negatives.values()), false_negatives)
	print("FP:", sum(false_positives.values()), false_positives)
	print() 

	for i in sorted(labels):
		if true_positives[i] == 0:
			fscore = 0
			print("fscore = 0")
		else:
			precision = true_positives[i] / float(true_positives[i]+false_positives[i])
			recall = true_positives[i] / float(true_positives[i]+false_negatives[i])
			fscore = 2 * (precision * recall) / float(precision + recall)
			print(i, 'fscore:',fscore,'precision:',precision,'recall',recall)
		
if __name__ == "__main__":
	main(sys.argv)
