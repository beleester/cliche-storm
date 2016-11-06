import random

import Corpus
from Corpus import Element,Trait,Problem
from WordCollection import WordCollection

def main():
##    text = ""
##    with open("test.txt") as file:
##        for line in file:
##            text += line
##    wc = WordCollection()
##    
##    wc.findElements(text)
    expandStory()

def expandStory():
    #Placeholder corpus
    world = World()
    plot = [Description("HERO"),
            AddProblem(),
            AddProblem(),
            AddProblem(),
            TheEnd()]

    #Go through the outline and expand each scene
    for scene in plot:
        print(scene.apply(world,plot))

#A World is the collection of all objects currently present in the story.
#Every Scene transforms the World and outputs text.
#A scene may also transform the plot (so it can create new scenes).
class World(object):
    def __init__(self):
        #Hero, villain, etc. are all Elements or subclasses
        self.hero = Corpus.getHero()
        self.villain = Corpus.getVillain()
        self.party = []
        self.NPCs = []
        #Not every subplot is resolved immediately
        #Problems enter the World and hang around until they're resolved.
        self.activeProblems = []

    def debug_print(self):
        print("Story status:")
        print("Dramatis Personae:")
        print("Protagonist:",str(self.hero))
        print("Antagonist:",str(self.villain))
        for npc in self.NPCs:
            print(str(npc))
        print("Important Objects:")
        for item in self.items:
            print(str(item))
        print("Ongoing Problems:")
        for prob in self.activeProblems:
            print(str(prob))

    def findElement(self,constraint):
        #Returns a random Element that meets the constraints.
        results = []
        if constraint == "HERO":
           results += [self.hero]
        elif constraint == "VILLAIN":
            results += [self.villain]
        elif constraint == "CHARACTER":
            results += [self.hero] + [self.villain] + self.party + self.NPCs
        elif constraint == "PARTY":
            results += [self.hero] + self.party
        elif constraint == "GOOD":
            results += self.hero + self.party
            for char in self.NPCs:
                if char.alignment > 0:
                    results += [char]
        elif constraint == "EVIL":
            results += self.hero + self.party
            for char in self.NPCs:
                if char.alignment < 0:
                    results += [char]

        #We may not have anything that fits, in which case the Scene needs to add one.
        if results == []:
            return None
        else:
            return random.choice(results)

    def findProblem(self,constraint=""):
        return random.choice(self.activeProblems)

#A Scene is a function that takes the World, transforms it, and returns text
#describing what happened.
#Scene is an abstract class and shouldn't be used directly.
class Scene(object):
    def __init__(self):
        pass

    def apply(self,world,plot):
        return "NO TEXT"

#Marker for the end of the story.
class TheEnd(Scene):
    def __init__(self):
        pass

    def apply(self,world,plot):
        return "The End."

#Outputs a description of an Element.
class Description(Scene):
    def __init__(self,constraint):
        self.constraint = constraint
    def apply(self,world,plot):
        #Find a random character meeting the constraint
        character = world.findElement(self.constraint)
        #Print their description.
        traits = list(character.traits)
        result = character.name + " is " + ", ".join([str(x) for x in traits[:-1]])
        result += " and " + str(traits[-1]) + "."
        return result

#Adds a new plot thread to the World. Inserts a SolveProblem somewhere later.
class AddProblem(Scene):
    def __init__(self,problem=None):
        self.problem = problem
        if problem == None:
            self.problem = Corpus.getProblem()

    def apply(self,world,plot):
        world.activeProblems.append(self.problem)
        startIndex = plot.index(self)
        endIndex = len(plot)
        insert = random.randint(startIndex+1,endIndex-1)
        plot.insert(insert,SolveProblem(self.problem))
        return "The heroes discovered that they had to " + self.problem.description + "."

#Resolving a problem removes it from the World.
#It MAY do any of the following:
#Add a trait to a character
#Add a Problem to the World
#Remove a trait from a character

#The resolution argument says what options are available for resolving the problem.
class SolveProblem(Scene):
    def __init__(self,problem,resolution=""):
        self.problem = problem
        self.resolution = resolution

    def apply(self,world,plot):
        #Choose a character trait to solve the problem.
        solver = world.findElement("PARTY")
        solveTrait = random.choice(list(solver.traits))
        #Choose a resolution type
        if self.resolution == "":
            self.resolution = random.choice(["POSITIVE","NEGATIVE"])

        #Describe the resolution
        result = "Because " + solver.name + " was " + solveTrait.description + ","
        if self.resolution == "POSITIVE":
            result += " they could " + self.problem.description + ". "
        else:
            result += " they failed to " + self.problem.description + ". "

        result += "As a result, "

        roll = random.randint(50,100)
        #Positive Resolutions:
        #20% chance of no result
        #80% chance of positive trait added
        if self.resolution == "POSITIVE":
            if roll <= 20:
                result += "the heroes continued their journey. "
            else:
                trait = Corpus.getPositiveTrait()
                solver.traits.add(trait)
                result += "they became " + trait.description + ". "

        #Negative Resolutions:
        #50% chance of negative trait
        #25% chance of new problem
        #25% chance of both
        else:
            if roll <= 50:
                trait = Corpus.getNegativeTrait()
                solver.traits.add(trait)
                result += "they became " + trait.description + ". "
            elif roll <= 75:
                newProblem = AddProblem()
                index = plot.index(self)
                plot.insert(index + 1,newProblem)
                result += "they now had to " + newProblem.problem.description + ". "
            else:
                trait = Corpus.getNegativeTrait()
                result += "they became " + trait.description + ". "
                newProblem = AddProblem()
                index = plot.index(self)
                plot.insert(index + 1,newProblem)
                result += "They also had to " + newProblem.problem.description + ". "
        
        return result

if __name__ == "__main__":
    main()

