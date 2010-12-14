#!/usr/bin/python

import random
import time
import sys
import yaml

"""
The Game object.
game.dumpfunction: Game-specific dump function (check oneforty.py)
game.extractfunction: Game-specific card extraction from .yml file function
"""
class Game:
    def __init__(self,dumpfunction,extractfunction):
        self.players = []        
        self.round = 0
        self.starttime = time.time()
        
        global dumpfn
        dumpfn = dumpfunction

        global extractfn
        extractfn = extractfunction
        
    """
    Ends the game with player:
     * victorious if 'win' is True
     * defeated if 'win' is False
     * tie if 'player' is None
    """
    def end_game(self,player,win):
        if (player is None):
            print "Game ended Draw!"
        else:
            other = find_other_player(player)
            if (win is True):
                print player.name + " is victorious!"
                print other.name + " has been defeated!"
            else:
                print other.name + " is victorious!"
                print player.name + " has been defeated!"
        print "Thanks for playing!"
        print "THE END!"
        sys.exit(0)

    """
    Returns the other player.
    """
    def find_other_player(self,player):
        for p in self.players:
            if (p != player):
                return p

"""
name: name of player
comment: comment
deckfname: deck filename
deck: deck struct
hand: the cards on the hand of the player 
graveyard: discarded cards
active: currently active cards. this may not be in use on all TCGs,
        we may have to move this in individual game modules
"""
class Player:
    def __init__(self, name, deckfname, comment):
        self.name = name
        self.comment = comment     
        self.deckfname = deckfname
        
        self.hand = []
        self.graveyard = []
        self.active = []
        
        print "[*] Created player: " + self.name + " # " + self.comment        

        self.deck = Deck(self)

    """
    Generator that gets us the next card off a pile of cards.
    """
    def gen_next_card(self,pile):
        while True: 
            for c in pile:
                yield c
        
    """
    General dumping function:
    'what' specifies what to dump. It's values can be:
    deck/hand/graveyard
    """
    def dump(self,what):
        global dumpfn
        
        if (what is 'deck'):
            print "Deck of " + self.name + ":"
            print "Name of deck: " + self.deck.name
            print "Cards: "
            map(dumpfn,self.deck.cards)
        elif (what is 'hand'):
            map(dumpfn,self.hand)            
        elif (what is 'graveyard'):
            map(dumpfn,self.graveyard)
        elif (what is 'locations'):
            map(dumpfn,self.locations)

    def flip_coin(self):
        return bool(random.randint(0,1))

    """
    Puts card from hand into graveyard.
    Caller must clear this from it's previous area.
    (iow he must remove it from his hand before discarding)
    """
    def discard_hand_card(self,card):
        if (not card):
            print "No card given to discard_hand_card()"
            return False
        self.hand.remove(card)
        self.graveyard.append(card)

    """
    Controller function.
    Selects a card from the player's hand.
    TODO, this sucks. This should be using either UI
    or have numbered cards.
    """
    def search_hand(self):
        gen = self.gen_next_card(self.hand)
        global dumpfn

        while True:
            c = gen.next()
            dumpfn(c)
            answ = query_yes_no("Use this card?", "no")
            if (answ == 'yes'):
                return c
            elif (answ == False):
                return None

    """
    Produces a numbered list of cards in 'cards'.
    Let's the user select one by it's number and
    then returns it. If no selection was made,
    return None. If no cards in stash, return False.
    """
    def select_card(self,cards):
        if not cards:
            return False
        
        global dumpfn
        gen = self.gen_next_card(cards)

        for i in range(len(cards)):
            print str(i) + ":"
            dumpfn(cards[i])
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
                print "Wrong input"
                return None
                
                
"""
Deck class.
deck.cards: list of cards in the deck
deck.data: yaml data of the deck file
deck.name: name of the deck
deck.player: player that the deck belongs to

* Shuffles deck

"""
class Deck:
    def __init__(self,player):
        self.player = player        
        self.data = self.open_deck_from_file(self.player.deckfname)        
        self.cards = []        
        self.name = self.data['name']
        
        global extractfn
        
        """
        * For every card in player's deck:
          / If it's quantity is great than 1, evaluate it multiple times.
           * Initiate it's Card object.
           * Populate it's stats with extractfn()
           * Append it to the players Deck.cards list.
        """        
        for carddata in self.data['cards']:
            i=carddata['quantity']
            while (i >= 1):
                card = Card(carddata,player)
                c = extractfn(card,carddata,player)
                self.cards.append(c)
                i -= 1

        # Shuffle deck
        self.shuffle_deck()
        
    def open_deck_from_file(self, fname):
        f = open(fname, 'r')
        data = yaml.load(f)
        f.close()
        return data

    # Shuffles deck
    def shuffle_deck(self):
        random.shuffle(self.cards)

    """
    Draws 'n' cards from the deck and puts them in our hand.
    Returns False if deck is empty (each game should handle
    deprived decks in it's own way, for example check
    draw_cards_oneforty in oneforty.py.)
    """
    def draw_cards(self,n):
        for c in range(n):
            if not self.cards: # if deck is empty
                return False
            self.player.hand.append(self.cards.pop(0))
        

    """
    Iterate deck 'till we find a card then if 'hand' is True
    put it in our hand, else just return it.
    This needs UI integration. TODO
    Implement it with python generator
    """
    def search_deck(self, hand):
        gen = self.player.gen_next_card(self.cards)
        while True:
            global dumpfn
            
            c = gen.next()
            dumpfn(c)
            answ = query_yes_no("Use this card?", "no")
            if (answ == 'yes'):
                if hand:
                    self.player.hand.append(c)
                else: 
                    return c
            elif (answ == False):
                return None
            
"""
name: card name
other elements are game dependant.
For example in 140, every card has attack and defence
"""
class Card:
    def __init__(self,card,player):
        self.name = card['name']
        self.descr = card['description']
        self.player = player

def query_yes_no(question, default="yes"):
    """ ~Ripped off the internets.~
    Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".

    Returns False for quit.
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n/q] "
    elif default == "yes":
        prompt = " [Y/n/q] "
    elif default == "no":
        prompt = " [y/N/q] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        elif choice == 'q': # quit query
            return False
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def print_stupid_line():
    print "---------------------"
    
