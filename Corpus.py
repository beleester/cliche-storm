import random

class Element(object):
    #Any noun in the story - a character, a location, a MacGuffin
    def __init__(self,name,tags=[],traits=[]):
        self.name = name #The word itself
        self.tags = tags #Labels that say where this word can be used.
        self.traits = traits #Adjectives that describe this word.
        self.alignment = 0 #Are they good or evil (from sentiment analysis?)

##    def join(self,other):
##        #Combines this Element with another, if they have the same or similar names.
##        if self.name != other.name and self.name not in other.name and other.name not in self.name:
##            return
##        if len(other.name) > len(self.name):
##            self.name = other.name
##        self.tags = self.tags.union(other.tags)
##        self.traits = self.tags.union(other.traits)


    def __eq__(self,other):
        if other == None:
            return False
        if self.name == other.name or self.name in other.name or other.name in self.name:
            return True
        return False

    def __hash__(self):
        return (hash(self.name) + sum([hash(tag) for tag in self.tags]) +
                sum([hash(trait) for trait in self.traits]) +
                hash(self.alignment))

    def __str__(self):
        return self.name + " " + str(self.tags)

class Trait(object):
    #Any adjective in the story.  Can be positive, negative, or neutral.
    #Should be able to finish an "is" statement
    #"a cool guy","crippled by an old injury","the owner of Excalibur"
    NEUTRAL=0
    POSITIVE=1
    NEGATIVE=2
    def __init__(self,description,align=NEUTRAL):
        self.description = description
        self.alignment = align

    def __eq__(self,other):
        return (self.description == other.description and self.alignment == other.alignment)

    def __hash__(self):
        return hash(self.description) + self.alignment

    def __str__(self):
        return self.description


global charCount
charCount = 0
#Problems are things that a hero can deal with.
#They can be constrained to a particular hero in case I want to make
#character-specific story arcs.
class Problem():
    def __init__(self,description,constraint=""):
        self.description = description
        self.constraint = constraint

def getHero():
    return Element("The Hero",
                   ["HERO","CHARACTER"],
                   [getNegativeTrait(),
                    getPositiveTrait()]
                   )

def getVillain():
    return Element("The Villain",["VILLAIN","CHARACTER"],
                   [Trait("wearing a black hat",Trait.NEGATIVE)]
                   )

def getNPC():
    global charCount
    charCount += 1
    return Element("NPC" + str(charCount),["CHARACTER"],
                   [Trait("totally normal",Trait.NEGATIVE)]
                   )

def getEvil():
    global charCount
    charCount += 1
    return Element("Goofus" + str(charCount),["CHARACTER","EVIL"],
                   [Trait("Wearing a black hat",align=Trait.NEGATIVE)]
                   )

def getGood():
    global charCount
    charCount += 1
    return Element("Gallant"+ str(charCount),["CHARACTER","GOOD"],
                   [Trait("Wearing a white hat",align=Trait.POSITIVE)]
                   )

def getPositiveTrait():
    traits = ["happy","cool","brave"]
    return Trait(random.choice(traits),Trait.POSITIVE)

def getNegativeTrait():
    traits = ["unhappy","lazy","cowardly"]
    return Trait(random.choice(traits),Trait.NEGATIVE)

def getNeutralTrait():
    return Trait("normal",Trait.NEUTRAL)

def getProblem():
    options = ["deliver the mail","fight the monster","find the MacGuffin","save the cat"]
    return Problem(random.choice(options))

def getMainProblem():
    options = ["slay the dragon","destroy the ring","find the Golden Fleece"]
    return Problem(random.choice(options))

def getLocation():
    locs = ["Rivendell","Mount Doom","Lothlorien"]
    return Element(random.choice(locs),tags=["LOCATION"])

def getElement(constraint):
    if constraint == "HERO":
       return getHero()
    elif constraint == "VILLAIN":
        return getVillain()
    elif constraint == "NPC":
        return getNPC()
    elif constraint == "LOCATION":
        return getLocation()
    elif constraint == "EVIL":
        return getEvil()
    elif constraint == "GOOD" or constraint == "PARTY":
        return getGood()
    else:
        raise Exception("Missing generator for " + constraint)
