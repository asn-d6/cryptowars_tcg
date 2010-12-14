#!/usr/bin/python

import sys
from pytcg import *

class Oneforty(Game):
    def __init__(self):
        print "Starting a fine game of 140.\n"        
        Game.__init__(self,self.dump_card,self.extract_oneforty_stats)
        
        self.maxrounds = 10
        
        self.initgame()
        self.startgame()
        
    """
    Takes a yaml card in 'data' a card in 'card'
    and populates the card.attack and card.defence
    based on 140's rules.
    """
    def extract_oneforty_stats(self,card,data):
        card.attack = data['attack']
        card.defence = data['defence']

    """Dump card function specific for the 140 game"""
    def dump_card(self,card):
        print "Name: " + card.name
        print "\tAttack: " + str(card.attack)
        print "\tDefence: " + str(card.defence)        

    def initgame(self):
       print "How many players? Assuming 2 for now.\n"
       # Hardcoded filenames
       self.players.append(Player("alice", "./d1.deck", "Lady of Salt")) # Player 1
       self.players.append(Player("bob",  "./d2.deck", "King In Yellow")) # Player 2

       print 
           
    """
    Starts a game of 140.
    """
    def startgame(self):
        print "-----------------"
        print "Starting game!\n\n"
        p1score = 0
        p2score = 0
        
        if (len(self.players[0].deck.cards) != len(self.players[0].deck.cards)):
            print "You don't have the same amount of cards in your deck. Play fair."
            sys.exit(-1)
            
        nr = len(self.players[0].deck.cards)

        while (self.round < self.maxrounds):
            if (self.round < nr):
                print "Starting " + str(self.round) + " round!"                
                """testing ground"""
                print "\nP1 choose your card: "
                p1card = self.players[0].deck.search_deck(False)
                print "\nP2 choose your card: "                
                p2card = self.players[1].deck.search_deck(False)                
                print 
                
                if (self.oneforty_battle(p1card,p2card) is 1):
                    p1score = p1score + 1
                else:
                    p2score = p2score + 1
                print "Score is: " + str(p1score) + ":" + str(p2score) + "!\n"
                self.round = self.round + 1
            else: #let's see who won
                if (p1score is p2score):
                    print "It's a tie!"
                    sys.exit(0)
                if (p1score < p2score):
                    print self.players[0].name + " won!" 
                else:
                    print self.players[1].name + " won!" 
                sys.exit(0)

    
    def draw_cards_oneforty(self,n,deck):
        if (deck.draw_cards(n) is False):
            print deck.player.name + " has deprived his/her deck!"            
            self.end_game(deck.player,False)
        
        
    """
    Adds attack and defence of each card and compares them.
    If it's a tie, c1 wins. Life is cruel.
    """
    def oneforty_battle(self,c1,c2):
        print "Battle between " + c1.name + " and " + c2.name + "!"
        if (c1.attack + c1.defence <= c2.attack + c2.defence):
            print c1.name + " won!"            
            print self.players[0].name + " won this battle!"
            return 1
        else:
            print c2.name + " won!"            
            print self.players[1].name + " won this battle!"            
            return 2

def main():
    # hardcoded
    game_type = 'oneforty'
    if game_type is 'oneforty':
        g = Oneforty()
    
if __name__ == "__main__":
        main()

        
