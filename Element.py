class Element(object):
    #Any noun in the story - a character, a location, a MacGuffin
    def __init__(self,name):
        self.name = name #The word itself
        self.tags = [] #Labels that say where this word can be used.
        self.attrs = [] #Adjectives that describe this word.
        self.rating = 0 #Score provided by sentiment analysis.

    def __eq__(self,other):
        if self.name == other.name or self.name in other.name or other.name in self.name:
            return True
        return False

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
