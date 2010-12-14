#!/usr/bin/python

import sys,random
sys.path.append("../")
from pytcg import *

"""
Game-specific card dumping methods and pyTCG wrappers.
"""
def dump_card(card):
    if (card.type == 'agent'): # agent cards don't have a Class.
        print "Name: " + card.name
        if (card.cost != 0):
            print "Cost: " + str(card.cost)
        print "Type: " + card.type
        if (card.action):
            print "Action: " + card.action
        print "Cipher: " + str(card.cipher)
        print "Intelligence: " + str(card.int)
        print "Evolution: " + str(card.evo)
        print "Attack: " + str(card.attack)
        print "Defence: " + str(card.defence)        
        print "Infiltration: " + str(card.infil)        
        print "Slots: " + str(card.slots)
        if (card.training > 0):
            print "Training: " + str(card.training)
        if (card.active):
            if (card.tapped):
                print "* Tapped"
            if (card.goingto != None):
                if (card.goingto != False):
                    print "* Travelling to " + card.goingto.name
                else:
                    print "* Travelling back to active area."
        print
    else: 
        card.dump(False)

def dump_cards(cards,enemy):
    if (not cards):
        return None
    if (type(cards).__name__ == "instance"): # one card    
        if (enemy and cards.hidden):
            print "* Hidden"
        else:
            dump_card(cards)
    else:
        if (enemy):
            for c in cards:
                if (not c.hidden):
                    dump_card(c)
                else:
                    print "* Hidden"
        else:
            for c in cards:
                dump_card(c)
            
                
        
"""
Produces a numbered list of cards in 'cards'.
Let's the user select one by it's number and
then returns it. If no selection was made,
return None. If no cards in stash, return False.
"""
def select_enemy_card(cards):
    if not cards:
        return False

    for i in range(len(cards)):
        print str(i) + ":"
        dump_cards(cards[i],True)
        print

    print "Select card or Enter to exit: "
    while True: 
        n = raw_input()
        try: 
            if (n==''):
                return None
            elif (int(n) in range(len(cards))):
                return cards[int(n)]
            else:
                print "Wrong input."
        except ValueError:
            print "Wrong input."
            return None
        
"""
Lets the player select a _friendly_ agent.
If tapped is True, then tapped agents can be selected as well.
"""
def select_agent(player,tapped):
    if not player.active:
        return False
    
    if tapped:
        for i in range(len(player.active)):
            print str(i) + ":"
            player.active[i].dump()
            print "Select agent or Enter to exit: "
            while True: 
                n = raw_input()
                if (n==''):
                    return None
                elif (int(n) in range(len(player.active))):
                    return player.active[int(n)]
                else:
                    print "Wrong input."
    else: 
        print_stupid_line()
        print "Tapped Agents: "
        for i in range(len(player.active)):
            if (player.active[i].tapped):
                player.active[i].dump()
        print_stupid_line()
    
        if (all_agents_tapped(player)):
            print "All agents are tapped."
            return False

        selection = []
        n=0
        for i in range(len(player.active)):
            if (not player.active[i].tapped):
                print str(n) + ":"            
                player.active[i].dump()
                selection.append(player.active[i])
                n+=1
    
        print "Select agent or Enter to exit: "
        while True: 
            n = raw_input()
            if (n==''):
                return None
            elif (int(n) in range(len(selection))):
                return selection[int(n)]
            else:
                print "Wrong input."
            
"""
This function allows the 'player' to select a deployed agent of his.
If 'attackers' is True, it presents the user with his attacking agents,
otherwise it presents the user with his guards
"""
def select_deployed_agent(inst,player,attackers):
    choice = []
    if (attackers):
        other = inst.find_other_player(player)
        for loc in other.locations:
            for a in loc.attackers:
                choice.append(a)
    else:
        for loc in player.locations:
            for g in loc.guards:
                choice.append(g)
    if (not choice):
        return False
    for i in range(len(choice)):
        print str(i) + ":"
        dump_card(choice[i])

    print "Select agent or Enter to exit: "
    while True: 
        n = raw_input()
        if (n==''):
            return None
        elif (int(n) in range(len(choice))):
            return choice[int(n)]
        else:
            print "Wrong input."
            
    
"""
Returns true if all agents are tapped, else
returns false.
"""
def all_agents_tapped(player):
    t=-1
    for i in range(len(player.active)):
        if (player.active[i].tapped):
            t += 1
    if (t==i): # all agents are tapped
        return True
    else:
        return False
        
        
    
"""
draw_cards() wrapper for cryptowars
"""
def draw_cards_crypto(n,deck):
    if (deck.draw_cards(n) is False):
        print deck.player.name + " has deprived his/her deck!"
        end_game(deck.player,False)
            
"""
Presents the user with options.
"""
def game_menu(inst,player):
    other = inst.find_other_player(player)
    while 1:
        print "Please enter your action: h/a/l/g/t/r/A/L/G/T/R/u/s/S/e/?"
        i = raw_input()
        if (i == "h"):
            print_stupid_line()
            print "Cards in hand: \n"
            player.dump('hand')
            print_stupid_line()                
        elif (i == "a"):
            print_stupid_line()                
            print "Dumping agents: \n"            
            for a in player.active:
                a.dump(False) 
            print_stupid_line()                
        elif (i == "l"):
            print_stupid_line()
            print "Location cards: \n"
            dump_cards(player.locations,False)
            print_stupid_line()            
        elif (i == "g"):
            print_stupid_line()                
            print "Cards in graveyard: \n"
            player.dump('graveyard')
            print_stupid_line()                
        elif (i == "t"):
            print_stupid_line()                
            print "Agents travelling: \n"
            dump_cards(player.travelling,False)
            print_stupid_line()                
        elif (i == "r"):
            print_stupid_line()
            print "Dumping rogue agents: \n"
            dump_cards(player.rogues,False)
            print_stupid_line()
        elif (i == "A"):
            print_stupid_line() 
            print "Dumping enemy agents: \n"
            for a in other.active:
                a.dump(True) 
            print_stupid_line()
        elif (i == "L"):
            print_stupid_line() 
            print "Enemy location cards: \n"
            for l in other.locations:
                l.dump(True)
            print_stupid_line()
        elif (i == "G"):
            print_stupid_line()                
            print "Cards in enemy graveyard: \n"
            dump_cards(other.graveyard,True)
            print_stupid_line()                
        elif (i == "T"):
            print_stupid_line()                
            print "Enemy travelling agents: \n"
            dump_cards(other.travelling,True)
            print_stupid_line()                
        elif (i == "R"):
            print_stupid_line()
            print "Dumping enemy rogue agents: \n"
            dump_cards(other.rogues,False)
            print_stupid_line()
        elif (i == "g"):
            print_stupid_line()                
            player.dump('graveyard')
            print_stupid_line()                
        elif (i == "u"):
            print_stupid_line()                
            print "We are on round " + str(inst.round)
            print_stupid_line()                
        elif (i == "s"):
            print_stupid_line()
            print "You currently have " + str(player.curareaslots) + "/" + str(player.areaslots) + " slots available"
            print_stupid_line()
        elif (i == "e"):
            print "Available entropy: " + str(player.entropy)
        elif (i == "?"):
            print """
                h: dump hand
                a: dump active area
                l: dump locations
                g: dump graveyard
                t: dump travelling agents
                r: dump rogue agents
                A: dump enemy active area
                L: dump enemy locations
                G: dump enemy graveyard
                T: dump enemy travelling agents
                R: dump enemy rogue agents
                u: print current round
                s: print available slots
                e: print available entropy
                ?: this menu
                Enter to proceed
                """
        elif (i==""):
            break
        else:
            continue
        
def untap_all_agents(player):
    for a in player.agents:
        a.tapped = False
