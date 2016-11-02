import nltk

from Element import Element

class WordCollection(object):
    def __init__(self):
        self.elements = []
    def findElements(self,text):
        sentences = nltk.tokenize.sent_tokenize(text)
        print(str(len(sentences)) + " sentences to process")
        progress = 0
        for sentence in sentences:
            #Tokenize and tag the sentence.
            tags = nltk.pos_tag(nltk.word_tokenize(sentence))
            #chunks = nltk.ne_chunk(tags).subtrees(filter=lambda x:x.label() == "LOCATION" or x.label() == "PERSON" or x.label() == "GPE")
            #for c in chunks: print(c.label() + " " + str(c.leaves()))
            #Find proper nouns.
            isProper = False
            index = 0
            while index < len(tags):
                #Group adjacent proper nouns into single objects.
                #Scan forwards as long as we've got more proper nouns.
                fullName = ""
                isProper = False
                while index < len(tags) and (tags[index][1] == "NNP" or tags[index][1] == "NNPS"):
                    fullName += tags[index][0] + " "
                    index += 1
                if fullName != "":
                    isProper = True
                index += 1

                #Do analysis on the containing sentence.  Is it a person or place?
                if isProper:
                    el = Element(fullName)
                    #Avoid redundant names - "Bilbo" and "Bilbo Baggins" should be combined.
                    if el in self.elements:
                        found = self.elements.index(el)
                        if len(el.name) > len(self.elements[found].name):
                            self.elements[found].name = el.name
                    else:
                        self.elements += [el]
            progress += 1
            if progress % 100 == 0: print(str(progress) + "/" + str(len(sentences)))
            
        for el in self.elements:
            print(str(el))
