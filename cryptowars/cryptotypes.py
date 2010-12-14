4#!/usr/bin/python

import sys,random
sys.path.append("../")
from pytcg import *

class Location:
    def __init__(self,card,player):
        self.player = player
        
        self.type = card.type
        self.name = card.name
        self.diff = card.diff
        self.trac = card.trac
        self.slots = card.slots
        self.hidden = True
        self.cost = card.cost
        self.action = card.action
        self.destroyrounds = False # Rounds 'till the Location gets destroyed
        
        self.guards = []
        self.attackers = []
        self.ontheroad = []

    def dump(self,enemy=False):
        if (enemy and self.hidden):
            print "* Hidden"
        else: 
            print "Name: " + self.name
            if (self.cost != 0):
                print "Cost: " + str(self.cost)
            print "Type: " + self.type
            if (self.action):
                print "Action: " + self.action
            
            print "Slots: " + str(self.slots)
            print "Difficulty: " + str(self.diff)
            print "Tractability: " + str(self.trac)
            if (not enemy):
                if (self.guards):
                    for a in self.guards:
                        print "[G] Guards: "
                        a.dump(False)
                if (self.attackers):
                    for a in self.attackers:
                        if (not a.hidden):
                            print "[A] Attackers: "
                            a.dump(False)
            else:
               if (self.attackers):
                   for a in self.attackers:
                       print "[A] Attackers"
                       a.dump(False)
               if (not self.hidden and self.guards):
                   for a in self.guards:
                       print "[G] Guards: "
                       a.dump(True)

    def destroy(self):
        print "Destroying location " + self.name + "..."
        if (self.guards):
            print "There are currently " + str(len(self.guards)) + " guards in " + self.name
            for g in self.guards:
                self.guards.remove(g)
                g.fallback(True)
                print "Guard " + g.name + " retreated."
        if (self.attackers):
            print "There are currently " + str(len(self.attackers)) + " attackers in " + self.name
            for a in self.attackers:
                self.attackers.remove(a)
                a.fallback(True)
                print "Attacker " + a.name + " retreated."                
        if (self.ontheroad):
            print "There are currently " + str(len(self.ontheroad)) + " travelling\
agents to " + self.name
            for t in self.ontheroad:
                self.ontheroad.remove(t)
                t.fallback(True)
                print "Travelling agent " + t.name + " retreated."                                
        self.player.locations.remove(self)
        self.player.areaslots -= self.slots
        print "Location " + self.name + " destroyed succesfully!"

    def play(self):
        self.player.locations.append(self)
        self.player.areaslots += self.slots
        print "Location " + self.name + " played" 

    """
    Returns true if location was discovered by an agent
    If location was discovered, flip it face up. 
    """
    def discovered(self,agent):
        if (self.trac < agent.int + agent.infil):
            self.hidden = False
            return True
        else:
            return False

"""
Agents in cryptowars have five evolutions:
*
|- Pawn (Alice,Bob, etc.) Tier 1, Evolution 1
|
- Agent (Agent Alice, Agent Bob, etc.) Tier 1, Evolution 2
|
|- Agent, Level 2 (Agent Mallory, Agent Eve, etc.) Tier 2, Evolution 3
|
- Agent, Level 3 (Agent Mallory, Agent Eve, etc.) Tier 2, Evolution 4
|
|- Agent, Level 4 (Agent Trent, etc.) Tier 3, Evolution 5
*

Initially agents start as pawns.
They become agents when they train their pawn's .training cost. (

agent.goingto: When agent is travelling 'goingto' tells us the location to where
he is heading. If None, he is stationary (either in active area or rogue) If False,
he is going back to his active area.

"""
class Agent:
    """
    This function generates a random *pawn* for the user and puts it into play
    Cost for pawn is 100 entropy.
    Stats of pawn is: Cipher/key: DES
                      Intelligence: 2-4
    """
    def __init__(self,player):
        self.player = player
        self.player.curareaslots += 1
        self.title = random.choice(["Alice", "Bob","Carol","Charlie","Dave"])
        self.name = self.title
        self.attack = random.randint(1,20)
        self.defence = random.randint(1,20)        
        ciphers = ["Vinegere","DES","3DES","TEA"]
        self.cipher = random.choice(ciphers)
        self.int = random.randint(1,20)
        self.evo = 1 # Evolution level of agent. Pawns get 1.
        self.tapped = True # Pawns come into play tapped
        self.loc = None
        self.infil = random.randint(1,20)         
        self.cost = 0
        self.slots = 1
        self.type = "agent"
        self.action = ""
        self.rounds = 1 # Rounds inside an enemy base 
        self.hidden = True
        self.goingto = None
        self.found = False
        self.equip = []
        self.rogue = False
        self.player.agents.append(self)
        self.active = True # TOFIX
        self.training = 2 # turns to become tier 1.5 
        self.traintokens = 0 # current train tokens
        self.alreadytrained = False
        
        print "\nGenerated: "
        self.dump(False)
        
    """
    Implementation of train action for agents.
    Increases traintokens by one, and taps the agent.
    """
    def train(self):
        if (self.alreadytrained):
            return False
        self.traintokens += 1
        self.alreadytrained = True
        self.tap()
        print self.title + " trained. Current train tokens: " + str(self.traintokens)
        

    """
    This function upgrades this agent.
    If card is None, then the upgrade is half a tier (ie. pawn -> agent)
    Else, 'card' is the agent card used to upgrade.
    Returns False if not enough train tokens on agent.
    """
    def upgrade(self,card=None):
        if card:
            if (card.training > self.traintokens):
                print "Not enough train tokens to upgrade to " + card.name
                return False
            self.traintokens -= card.training
            self.training = 4
            self.title = "Agent " + card.name
            self.evo = card.evo
            self.cipher = card.cipher
            self.int =  card.int
            self.attack = card.attack
            self.defence = card.defence
            self.slots = card.slots
            self.hidden = True
        else:
            if (self.training > self.traintokens):
                print "Not enough train tokens to upgrade."
                return False                
            self.traintokens -= self.training
            if (self.evo == 1):
                self.title = "Agent " + self.title
                self.cipher = "3DES"
                self.training = 0
            elif (self.evo == 3):
                self.cipher = "AES-ECB 128"
                self.title = "Operative" + self.title.strip("Agent")
                self.training = 0
            self.evo = self.evo+1
            # self.cipher = self.cipher
            self.int += random.randint(1,20)
            self.attack += random.randint(1,20)
            self.defence += random.randint(1,20)
            self.infil = random.randint(1,30)
            self.hidden = True
        return True

    """
    This function dumps an agent to the screen.
    If 'enemy' is True, the agent to be dumped is
    hostile and some info must be hidden
    """
    def dump(self,enemy=False):
        if (enemy and self.hidden):
           print "* Hidden"
        else:           
            print "Name: " + self.title
            if (self.cost != 0):
                print "Cost: " + str(self.cost)
            print "Type: " + self.type
            if (self.action):
                print "Action: " + self.action
            print "Cipher: " + str(self.cipher)
            print "Intelligence: " + str(self.int)
            print "Evolution: " + str(self.evo)
            print "Attack: " + str(self.attack)
            print "Defence: " + str(self.defence)        
            print "Infiltration: " + str(self.infil)
            print "Slots: " + str(self.slots)
            if (self.training > 0):
                print "Training: " + str(self.training)
            if (self.traintokens > 0):
                print "Cur. Training Tokens: " + str(self.traintokens)        
            if (self.tapped):
                print "* Tapped"
            if (self.goingto != None):
                if (self.goingto != False):
                    print "* Travelling to " + self.goingto.name
                else:
                    print "* Travelling back to active area."
            
    def tap(self):
        self.tapped = True
    
    def untap(self):
        self.tapped = False

    """
    Rogue agents are agents that can't return to their active area after doing a job.
    They are vulnerable and attackable by the opponent and if captured the player gets
    damaged.
    """
    def become_rogue(self):
        self.rogue = True
        self.player.rogues.append(self)
        self.goingto = None
        self.player.travelling.remove(self)
        self.penalty = int(float(self.player.bits)/10)
        print "[Agent] " + self.title + " is now a rogue agent. If captured by the opponent "\
+ str(self.penalty) + " bits will be taken from the opponent."
        self.player.travelling.remove(self)

    """
    This function returns an agent to the active area.
    If there is a slot he is sent there, elsewise he becomes
    a rogue agent if he isn't already one.
    """
    def return_to_active_area(self):
        if (self.player.areaslots < self.player.curareaslots + self.slots):
            if (self.rogue == False):
                print "[Agent] No active area slots. Agent becomes rogue!"
                self.become_rogue()
            else:
                self.player.active.append(self)
                self.player.curareaslots += self.slots
                if (self in self.player.travelling):
                    self.player.travelling.remove(self)
                    
    def destroy(self):
        self.player.agents.remove(self)
        if (self.rogue):
            self.player.rogues.remove(self)
            print "Rogue agent " + self.title + " defeated. " + str(self.penalty) + "\
 substracted from the opponent"
            self.player.bits -= self.penalty
        else:
            print self.title + " destroyed."
    
    """
    When an agent is travelling to a location, he initially
    gets added to the 'ontheroad' list of that location.
    He is added to the 'travelling' agent list of that player
    and he gets tapped.
    The location is noted to the agent's 'goingto'.
    """
    def travel(self,loc):
        loc.ontheroad.append(self)
        self.player.travelling.append(self)
        self.goingto = loc
        if (loc.player == self.player):
            print self.title + " is now travelling towards " + loc.name
        else:
            if (loc.hidden):
                print self.title + " is now travelling."
            else:
                print self.title + " is now travelling towards " + loc.name                     
    """
    Executed when an agent has to return to the active area after his
    job is done.
    If 'travelling' spend a travelling round.  
    """
    def fallback(self,travelling):
        self.goingto = False
        if (travelling):
            self.player.travelling.append(self)
        
    """
    Executed when an agent reaches it's destination.
    """
    def finish_travel(self,loc):
        self.goingto.ontheroad.remove(self)
        self.player.travelling.remove(self)
        self.goingto = None
        
class Technology:
    def __init__(self,card,player):
        self.name = card.name
        self.type = card.type
        self.action = card.action
        self.cost = card.cost
        self.turns = 1 # Turns in game
        self.hidden = True

    def dump(self,enemy=False):
        print "Name: " + self.name
        if (self.cost != 0):
            print "Cost: " + str(self.cost)
        print "Type: " + self.type
        if (self.action):
            print "Action: " + self.action
        if (self.turns > 1):
            print "Turns: " + str(self.turns)
                
        
class Equipment:
    def __init__(self,card,player):
        self.name = card.name
        self.type = card.type
        self.action = card.action
        self.player = player
        self.cost = card.cost
        self.bearer = None
        self.hidden = True
        
    def attach(self,agent):
        self.bearer = agent
        agent.equip.append(self)
        #evaluate_action(self.action) ???

    def dump(self,enemy=False):
        print "Name: " + self.name
        if (self.cost != 0):
            print "Cost: " + str(self.cost)
        print "Type: " + self.type
        if (self.action):
            print "Action: " + self.action
        if (self.bearer): 
            print "Bearer: " + self.bearer

        
