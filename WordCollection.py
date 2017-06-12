import nltk
import operator

from Corpus import Element

class WordCollection(object):
    def __init__(self):
        self.elements = []
    def findElements(self,text):
        sentences = nltk.tokenize.sent_tokenize(text)
        print(str(len(sentences)) + " sentences to process")
        progress = 0
        chunkFreq = {}
        for sentence in sentences:
            #Tokenize and tag the sentence.
            tags = nltk.pos_tag(nltk.word_tokenize(sentence))
            #Identify named entities.
            chunks = nltk.ne_chunk(tags).subtrees(filter=lambda x:x.label() != "S")
            #Store the entities as Elements
            for c in chunks:
                #Combine all the proper nouns into one name.
                fullName = " ".join([x[0] for x in c.leaves()])
                el = Element(fullName)
                #Count how often we get a label.
                if fullName in chunkFreq:
                    if c.label() in chunkFreq[fullName]:
                        chunkFreq[fullName][c.label()] += 1
                    else:
                        chunkFreq[fullName][c.label()] = 1
                else:
                    chunkFreq[fullName] = {}
                    chunkFreq[fullName][c.label()] = 1
                    
                if el not in self.elements:
                    self.elements += [el]

            progress += 1
            if progress % 100 == 0: print(str(progress) + "/" + str(len(sentences)))

        #Decide on which label we believe, if we got multiples.
        for el in self.elements:
            #Find the most frequent label
            sortedLabels = sorted(chunkFreq[el.name].items(), key=operator.itemgetter(1))
            label = sortedLabels[0][0]
            #The NE chunker is good at recognizing people and locations, not so good at others.
            #So we'll just assume that anything that isn't one of those is an "OBJECT"
            if label == "PERSON" or label == "LOCATION":
                el.tags.add(label)
            else:
                el.tags.add("OBJECT")
        for el in self.elements:
            print(str(el))
