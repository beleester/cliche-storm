import random

class Element(object):
    #Any noun in the story - a character, a location, a MacGuffin
    def __init__(self,name,tags=set(),traits=set()):
        self.name = name #The word itself
        self.tags = tags #Labels that say where this word can be used.
        self.traits = traits #Adjectives that describe this word.
        self.alignment = 0 #Are they good or evil (from sentiment analysis?)

    def join(self,other):
        #Combines this Element with another, if they have the same or similar names.
        if self.name != other.name and self.name not in other.name and other.name not in self.name:
            return
        if len(other.name) > len(self.name):
            self.name = other.name
        self.tags = self.tags.union(other.tags)
        self.traits = self.tags.union(other.traits)


    def __eq__(self,other):
        if self.name == other.name or self.name in other.name or other.name in self.name:
            return True
        return False

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

    def __str__(self):
        return self.description

class Problem():
    def __init__(self,description):
        self.description = description

def getHero():
    return Element("The Hero",
                   set({"HERO","CHARACTER"}),
                   set({Trait("flawed",Trait.NEGATIVE),
                        Trait("cool",Trait.POSITIVE)})
                   )

def getVillain():
    return Element("The Villain",set({"VILLAIN","CHARACTER"}),
                   set({Trait("wearing a black hat",Trait.NEGATIVE)})
                   )

def getNPC():
    return Element("An NPC",set({"CHARACTER"}),
                   set({Trait("just a guy",align=Trait.NEUTRAL)})
                   )

def getPositiveTrait():
    return Trait("happy",Trait.POSITIVE)

def getNegativeTrait():
    return Trait("unhappy",Trait.NEGATIVE)

def getTrait():
    return Trait("some kinda guy",Trait.NEUTRAL)

def getProblem():
    return Problem(getProblemDescription())

def getProblemDescription():
    return random.choice(["deliver the mail","slay the dragon","destroy the ring"])
