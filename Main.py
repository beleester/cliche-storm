import random

import Corpus
from Corpus import Element,Trait,Problem
from WordCollection import WordCollection
import re

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
    world = World()
    plot = [Description(world.hero), #Opening Image
            AddFlaw(), #Setup
            AddMainProblem(), #Catalyst
            Debate(), #Debate
            Threshold(), #Threshold
            AddProblem(constraint="GOOD"), #B Plot
            FunAndGames(), #Fun and Games
            Interaction("POSITIVE"),
            Midpoint(), #Midpoint
            BadGuyClosesIn(), #Bad Guy Closes In
            AllIsLost(), #All Is Lost
            Interaction("NEGATIVE"), #Long Night of the Soul
            Interaction("POSITIVE"), #Eureka Moment
            RemoveFlaw(),
            SolveMainProblem(), #Finale
            SolveAllProblems(),
            Description(world.hero), #Final Image
            TheEnd()
            ]
    #Go through the outline and create the list of Problems.
    for scene in plot:
        scene.apply(world,plot)
    #After we've outline the scenes, go back and make sure that
    #every Element is introduced before it's used.
    allPrereqs = set()
    for i in range(len(plot)):
        scene = plot[i]
        if hasattr(scene,"prereqs"):
            for prereq in scene.prereqs:
                allPrereqs.add(prereq)
    for prereq in allPrereqs:
        slot = findOpenSlot(plot,i)
        scene = Description(prereq)
        plot.insert(slot,scene)
        scene.apply(world,plot)
        #print("Introduced " + prereq.name + " at " + str(slot))

    #Once this is done, output the finished story.
    for scene in plot:
        print(type(scene).__name__,scene.text)

#Finds all $-delimited strings in a setting and fills them in
#with things in the world. May introduce new elements into the world.
def makeReplacements(string,world,newFrequency=0.5):
    matches = re.findall("\$(.*?)\$",string)
    result = []
    for tag in matches:
        element = replacement(tag,world,newFrequency)
        #Now get the location of the tag in the string so we can cut it out.
        match = re.search("\$(.*?)\$",string)
        string = string[:match.start()] + element.name + string[match.end():]
        result += [element]
        
    return string,result

def replacement(string,world,newFrequency=0.5):
    #Makes a single replacement using something in the world.
    shouldAddNew = random.random()
    element = world.findElement(string,createIfMissing=True)
    #Hero and Villain are unique, we shouldn't generate new ones.
    if shouldAddNew < newFrequency and string != "HERO" and string != "VILLAIN":
        return Corpus.getElement(string)
    else:
        return element

#Finds a place that an Element can be introduced without infodumping.
#Does this by picking a random point before the given index, while avoiding
#spots near other introductions
def findOpenSlot(plot,before):
    slots = list(range(before))
    for i in range(before):
        if type(plot[i]).__name__ == "Description":
            #Remove the slots both before and after the introduction
            if i in slots: slots.remove(i)
            if i+1 in slots: slots.remove(i+1)
    if len(slots) > 0:
        return random.choice(slots)
    else: #If we have too many things to introduce, just pick any slot.
        return random.choice(range(before))
    

def getInsertionPoints(start,end,count):
    #Given two indexes, generates n random locations you can insert something,
    #such that everything inserted remains between the two items that
    #you want to insert between, accounting for the list's expansion.
    result = []
    for i in range(count):
        result += [random.randint(start+1,end)]
        end = end + 1
    return result
    
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
        self.other = []
        #Not every subplot is resolved immediately
        #Problems enter the World and hang around until they're resolved.
        self.activeProblems = []
        #The main story arc gets advanced at specific points in the beat sheet.
        self.mainProblem = None
        #The World Tension is a universal setting for how often bad things should happen.
        self.tension = 0.5 #Initially, problems are 50-50 good or bad resolutions.

    def debug_print(self):
        print("Story status:")
        print("Dramatis Personae:")
        print("Protagonist:",str(self.hero))
        print("Antagonist:",str(self.villain))
        for npc in self.NPCs:
            print(str(npc))
        print("Ongoing Problems:")
        for prob in self.activeProblems:
            print(str(prob))

    @property
    def allElements(self):
        return [self.hero] + [self.villain] + self.party + self.NPCs + self.other

    def findElement(self,*constraints,createIfMissing=True):
        #Returns a random Element that meets the constraints.
        results = []
        for constraint in constraints:
            if constraint == "HERO":
               results += [self.hero]
            elif constraint == "VILLAIN":
                results += [self.villain]
            elif constraint == "CHARACTER":
                results += [self.hero] + [self.villain] + self.party + self.NPCs
            elif constraint == "NPC":
                results += self.NPCs
            elif constraint == "PARTY":
                results += self.party
            #Hero, party, and any good-aligned NPCs
            elif constraint == "GOOD":
                results += [self.hero] + self.party
                for char in self.NPCs:
                    if char.alignment > 0:
                        results += [char]
            #Villain and any evil NPCs.
            elif constraint == "EVIL":
                results += [self.villain]
                for char in self.NPCs:
                    if char.alignment < 0:
                        results += [char]
                        
            #Search by trait
            elif constraint.startswith("TRAIT"):
                start = constraint.find("(") + 1
                end = constraint.find(")")
                traitDesc = constraint[start:end]
                for char in (self.allElements):
                    for trait in char.traits:
                        if traitDesc == trait.description:
                            results += [char]

        #We may not have anything that fits, in which case we should probably invent one.
        if results == []:
            if createIfMissing:
                #Add the new item to the lists.
                created = Corpus.getElement(constraint)
                if constraint == "PARTY":
                    self.party.append(created)
                elif constraint == "NPC":
                    self.NPCs.append(created)
                else:
                    self.other.append(created)
                
                return created
            else:
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
        self.prereqs = []
        self.text = ""
        return

    def apply(self,world,plot):
        self.text = "ERROR: NO TEXT"
        return
        

#Marker for the end of the story.
class TheEnd(Scene):
    def apply(self,world,plot):
        self.text = "The End."

#Outputs a description of an Element.
class Description(Scene):
    def __init__(self,element):
        self.element = element
        self.text = ""
    def apply(self,world,plot):
        #Print all their traits
        traits = list(self.element.traits)
        if len(traits) == 0:
            self.text = self.element.name + " had no interesting features."
        elif len(traits) > 1:
            self.text = self.element.name + " was " + ", ".join([str(x) for x in traits[:-1]])
            self.text += " and " + str(traits[-1]) + "."
        else:
            self.text += self.element.name + " was " + str(traits[0]) + "."

#Adds a new plot thread to the World. Inserts a SolveProblem somewhere later.
class AddProblem(Scene):
    #A specific problem can be passed in.
    #A problem can be constrained to only be solvable by some category of person.
    def __init__(self,endpoint=1,resolution="",constraint="",problem=None):
        self.endpoint = endpoint
        self.problem = problem
        if self.problem == None:
            self.problem = Corpus.getProblem()
        self.constraint = constraint
        self.resolution=resolution

    def apply(self,world,plot):
        self.text = "The heroes discovered that they had to " + self.problem.description + "."
        
        world.activeProblems.append(self.problem)
        startIndex = plot.index(self)
        endIndex = startIndex + self.endpoint
        insert = random.randint(startIndex+1,endIndex)
        plot.insert(insert,SolveProblem(self.problem,resolution=self.resolution,
                                        constraint=self.constraint))

#Resolving a problem removes it from the World.
#It MAY do any of the following:
#Add a trait to a character
#Add a Problem to the World
#Remove a trait from a character

#The resolution argument says what options are available for resolving the problem.
class SolveProblem(Scene):
    def __init__(self,problem,resolution="",constraint="PARTY"):
        self.problem = problem
        self.resolution = resolution
        self.constraint = constraint
        self.prereqs = []

    def apply(self,world,plot):
        if self.problem in world.activeProblems:
            world.activeProblems.remove(self.problem)
        #Choose a character trait to solve the problem.
        solver = world.findElement("PARTY",createIfMissing=True)
        self.prereqs += [solver]
        solveTrait = random.choice(list(solver.traits))
        #Choose a resolution type, if one hasn't been picked for us.
        if self.resolution == "":
            roll = random.random()
            if roll < world.tension:
                self.resolution = "POSITIVE"
            else:
                self.resolution = "NEGATIVE"
        #Describe the resolution
        self.text = "Because " + solver.name + " was " + solveTrait.description + ","
        if self.resolution == "POSITIVE":
            self.text += " they could " + self.problem.description + ". "
        else:
            self.text += " they failed to " + self.problem.description + ". "

        self.text += "As a result, "

        roll = random.random()
        #Positive Resolutions:
        #20% chance of no result
        #80% chance of positive trait added
        if self.resolution == "POSITIVE":
            if roll <= 0.2:
                self.text += "the heroes continued their journey. "
            else:
                trait = Corpus.getPositiveTrait()
                solver.traits.append(trait)
                self.text += "they became " + trait.description + ". "

        #Negative Resolutions:
        #50% chance of negative trait
        #25% chance of new problem
        #25% chance of both
        else:
            if roll <= 0.5:
                trait = Corpus.getNegativeTrait()
                solver.traits.append(trait)
                self.text += "they became " + trait.description + ". "
            elif roll <= 0.75:
                #Sudden unplanned problems shouldn't last too long.  Long enough to loom a bit,
                #not so long that they take over the story.
                newProblem = AddProblem(endpoint=3) 
                index = plot.index(self)
                plot.insert(index + 1,newProblem)
                self.text += "they now had to " + newProblem.problem.description + ". "
            else:
                trait = Corpus.getNegativeTrait()
                self.text += "they became " + trait.description + ". "
                newProblem = AddProblem(endpoint=3)
                index = plot.index(self)
                plot.insert(index + 1,newProblem)
                self.text += "They also had to " + newProblem.problem.description + ". "

class AddFlaw(Scene):
    def apply(self,world,plot):
        flaw = Corpus.getNegativeTrait()
        world.hero.traits.append(flaw)
        world.flaw = flaw
        self.text = world.hero.name + " had a problem. He was " + flaw.description + ". "

class RemoveFlaw(Scene):
    def apply(self,world,plot):
        flaw = world.flaw
        world.hero.traits.remove(flaw)
        self.text = world.hero.name + " overcame his " + flaw.description + ". "

class AddMainProblem(Scene):
    #A main problem is a series of related Problems.
    #AddMainProblem inserts those problems into the story in a logical way.
    #This only covers the first act - Midpoint, BadGuyClosesIn, and AllIsLost will insert additional problems.
    def apply(self,world,plot):
        world.mainProblem = Corpus.getMainProblem()
        result = "The heroes had to " + world.mainProblem.description

        #Only a few random challenges at the start, because we have the Debate and Threshold to get through as well.
        numTasks = random.randint(1,2)
        start = plot.index(self)
        end = start + 4 #Insert problems between here and FunAndGames()
        for point in getInsertionPoints(start,end,numTasks):
            plot.insert(point,MinorProblem())

class MinorProblem(Scene):
    #A problem that can be handled in one scene
    #(or currently, one sentence).
    tasks = ["pass through $LOCATION$",
             "meet with $NPC$",
             "defeat $EVIL$"]
    def __init__(self,resolution="",constraint="PARTY"):
        self.resolution = resolution
        self.constraint = constraint
        self.prereqs = []
    def apply(self,world,plot):
        #Pick a random task
        task = random.choice(MinorProblem.tasks)
        task,elementsAdded = makeReplacements(task,world)
        self.prereqs += elementsAdded
        problem = Problem(task)
        #Add it to the world.
        index = plot.index(self)
        resolution = SolveProblem(problem)
        plot.insert(index + 1,resolution)
        
        #Create the text.
        self.text = "The heroes had to " + problem.description

class Debate(Scene):
    def apply(self,world,plot):
        self.text = world.hero.name + " hesitated, because they were " + random.choice(world.hero.traits).description + "."

class Threshold(Scene):
    def apply(self,world,plot):
        self.text = "The heroes entered the WORLD OF ADVENTURE!"

#Character interactions - because not everything is a battle to win.
class Interaction(Scene):
    def __init__(self,mood=""):
        if mood == "":
            #Interactions don't have to add traits, but they usually do.
            #0.6 positive, 0.3 negative, 0.1 neutral.
            roll = random.random()
            if roll < 0.6:
                self.mood = "POSITIVE"
            elif roll < 0.9:
                self.mood = "NEGATIVE"
        else:
            self.mood = mood
        
    def apply(self,world,plot):
        self.hero = world.hero
        self.partyMember = world.findElement("PARTY",createIfMissing=True)
        #Can talk about people or objectives
        roll = random.random()
        if roll < 0.2:
            subject = world.findElement("CHARACTER")
            self.text = self.hero.name + " and " + self.partyMember.name + " talked about " + subject.name + ". "
        else:
            subject = random.choice(world.activeProblems + [world.mainProblem])
            self.text = self.hero.name + " and " + self.partyMember.name + " talked about " + subject.description + ". "
        
        #Interactions can add traits - Heroic Pep Talks!
        if self.mood == "POSITIVE":
            trait = Corpus.getPositiveTrait()
            self.hero.traits.append(trait)
            self.text += "As a result, they became " + trait.description + ". "
        elif self.mood == "NEGATIVE":
            trait = Corpus.getNegativeTrait()
            self.hero.traits.append(trait)
            self.text += "As a result, they became " + trait.description + ". "
        
class FunAndGames(Scene):
    def apply(self,world,plot):
        #Add a bunch more problems on their adventure.
        numTasks = random.randint(4,6)
        start = plot.index(self)
        end = start + 4 #Insert problems between here and FunAndGames()
        for point in getInsertionPoints(start,end,numTasks):
            plot.insert(point,MinorProblem())
            
        self.text = "The heroes enjoyed their adventure at first..."

class Midpoint(Scene):
    def apply(self,world,plot):
        #The Midpoint is an extra-bad problem: Either a new ongoing problem,
        #or a major character death.
        #It also changes the World Tension to make problems worse.
        #Lastly, it generates the next batch of problems
        
        #Pick the big complication
        self.text = "Suddenly... "
        start = plot.index(self)
        end = start + 2 #Far enough to reach AllIsLost
        
        roll = random.random()
        if roll < 0.5:
            problem = AddProblem(endpoint=4)
            plot.insert(start+1,problem)
            end += 1
        else:
            victim = world.findElement("PARTY",createIfMissing=False)
            if victim == None:
                self.text += "The hero realized he was very, very alone."
            else:
                self.text += victim.name + " was killed by ninjas!"
                world.party.remove(victim)
        
        #Add a bunch more problems on their adventure.
        world.tension = 0.75
        numTasks = random.randint(4,6)
        end = start + 2
        for point in getInsertionPoints(start,end,numTasks):
            plot.insert(point,MinorProblem())
            
class BadGuyClosesIn(Scene):
    def apply(self,world,plot):
        #I don't actually know if this needs to be its own scene, or if it's
        #just a label for the stuff that happens after the midpoint.
        self.text = "Things got worse"
        
class AllIsLost(Scene):
    def apply(self,world,plot):
        self.text = "To make matters worse..."
        start = plot.index(self)
        #One last midpoint-esque problem
        roll = random.random()
        if roll < 0.5:
            problem = MinorProblem(resolution="NEGATIVE")
            plot.insert(start+1,problem)
        else:
            victim = world.findElement("PARTY",createIfMissing=False)
            if victim == None:
                self.text += "The hero realized he was very, very alone."
            else:
                self.text += victim.name + " was killed by ninjas!"
                world.party.remove(victim)
            
class SolveMainProblem(Scene):
    #The Hero solves the main problem.
    #At the moment, this just copies the SolveProblem() logic with the "Positive, gain trait" result.
    def apply(self,world,plot):
        #Choose a character trait to solve the problem.
        solver = world.findElement("HERO")
        solveTrait = random.choice(list(solver.traits))
        #Describe the resolution
        self.text = "Because " + solver.name + " was " + solveTrait.description + ","
        self.text += " they could " + world.mainProblem.description + ". "
        trait = Corpus.getPositiveTrait()
        solver.traits.append(trait)
        self.text += "they became " + trait.description + ". "
        self.text += "The villain was defeated! Huzzah!"
        
class SolveAllProblems(Scene):
    #If there are any problems still left open, somehow, solve them now.
    def apply(self,world,plot):
        self.text = ""
        for problem in world.activeProblems:
            self.text += "Buoyed by their victory, the heroes could also " + problem.description + ". "
    
##class IntroduceElement(Scene):
##    def __init__(self,element):
##        self.element = element
##
##    def apply(self,world,plot):
##        self.text
    
if __name__ == "__main__":
    main()

