#!/usr/bin/python

import sys,random
from misc import *
from cryptotypes import *
sys.path.append("../")
from pytcg import *

"""
Cryptowars game class:

The following elements are added to the player object:
player.baseentropy: Base entropy derived from the current active
                    entropy generators.
player.agents: Active agents of player.
player.technologies: Active technologies of each player.
player.bits: Bits remaining off player's privatekey.
player.entropy: Available player entropy


crypto.players: players
crypto.upkeepentropy: entropy per round (configurable)

NOTES: crypto wars won't be using pyctg's dump('active') because it's
active area is populated by agents that are not cards (contrary to
popular belief)
"""
class Crypto(Game):
    """
    Game initialization and creation methods.
    """
    def __init__(self):
        print "Starting a fine game of cryptowars.\n"        
        Game.__init__(self,dump_card,self.extract_crypto_stats)
        
        self.maxrounds = 20
        self.upkeepentropy = 100
        
        self.maxlocs = 7 # Max seven locations
        self.maxhand = 7 # Max seven cards in hand
        
        self.initgame()
        self.startgame()

    def initgame(self):
        print "How many players? Assuming 2 for now.\n"
        # Hardcoded filenames
        
        self.players.append(Player("alice", "./portents.deck", "Lady of Salt")) 
        self.players.append(Player("bob",  "./gawk.deck", "King In Yellow"))
        
        print 

        for p in self.players:
            p.entropy = 500 # Setting initial entropy
            p.baseentropy = 0 # Setting initial baseentropy
            p.cpu = 0 # Initial player CPU 
            p.bits = 512 # Setting initial key size
            p.tech = [] # Initializing technology list
            p.locations = [] # Initializing location list
            p.travelling = [] # Initializing travelling list
            p.rogues = [] # Rogue agents of player
            p.agents = []
            p.areaslots = 1 # Maximum slots for player's active area (initial: 1) 
            p.curareaslots = 0 # Current active area slots used
            p.pawngenround = False # Have we generated a pawn this round?
            
            draw_cards_crypto(5,p.deck)
        
           
    def startgame(self):
        print "[!] Starting game!\n\n"
        
        while (self.round < self.maxrounds):
            self.round += 1
            print "\n[*] Starting " + str(self.round) + " round!"
            self.crypto_round()
        print "\n[!] Rounds depleted ."
        player = self.players[0]
        other = self.find_other_player(player)
        print player.name + " remaining bits: " + str(player.bits)
        print other.name + " remaining bits: " + str(other.bits)
        if (player.bits > other.bits):
            self.end_game(player,True)
        elif (other.bits > player.bits):
            self.end_game(other,True)
        else:
            self.end_game(None,None)
        
    def crypto_round(self):
        for p in self.players:
            self.player_round(p)

    """
    Takes a yaml card in 'data' a card in 'card'
    and populates the card.attack and card.defence
    based on cryptowar's rules.
    """
    def extract_crypto_stats(self,card,data,player):
        try: 
            card.type = data['type']
            card.cost = data['cost']
            card.action = data['action'] # Action of card
            if (card.type == 'agent'): # Agent upgrades
                card.evo = data['evo'] # Evolution level of agent.
                card.cipher = data['cipher'] # Cipher this agent uses when
                                             # in a location. Defence.
                card.int = data['intelligence'] # Cryptanalytic skills of agent. Attack.
                card.infil = data['infiltration'] # Infiltritability of agent.
                card.attack = data['attack'] # Attack of agent
                card.defence = data['defence'] # Defence of agent
                card.slots = data['slots']
                card.training = data['training']
                card.active = False # is this card in play? TOFIX
            elif (card.type == 'location'): # Location cards.
                card.trac = data['traceability']
                card.diff = data['difficulty']
                card.slots = data['slots']
                return Location(card,player)
            elif (card.type == 'equipment'): # Equipment cards
                return Equipment(card,player)
            elif (card.type == 'technology'):
                return Technology(card,player)
            return card
            
        except KeyError:
            print "Faulty card detected."
            print "Proceeding..."
            
    def max_active_area_size(self,player):
        if (not player.locations):
            return 1
        size = 0
        for loc in player.locations:
            size += loc.slots
        return size
            
            
    """
    A cryptowars round:
    * Upkeep phase:
      Gain entropy.
      Upkeep effects
      Player draws one card.
      Agent arrival
      Stealth rolls 
      COllect rogue agents
    * Active phase:
      Players generate pawns (Alices/Bobs etc.) OR
      [Players may play cards from their hands.
      Players may train their agents.
      Players may promote their agents.
      (Players may deploy agents.)]
    * Battle phase:
      Detected combat.
    * Communication phase:
      Players may play cards from their hands.
      (Players may deploy agents.)
      Damage calculation for infiltrated agents 
    * End phase:
      'End of the round' effects take place.
       Player with more than 7 cards, discards cards.
    """
    def player_round(self,player):
        #Upkeep:
        print "\n"
        
        print_stupid_line()
        print player.name + "'s turn!"
        print "Private key bits remaining: " + str(player.bits)
        print_stupid_line()        
        print
        
        # Upkeep phase
        self.upkeep_phase(player)
        
        # Active phase
        self.active_phase(player)

        # Battle phase
        self.battle_phase(player)
        
        # Communication round
        self.comm_phase(player)
        
        self.end_phase(player)
        
        return True

    def end_phase(self,player):
        print "[E] End phase"

        # Yes, it's silly checking this here, but: TOFIX
        for p in self.players:
            if (p.bits <= 0):
                self.end_game(p,False)
                
        h = len(player.hand)
        while (h > self.maxhand): # Discard extra cards
            print "You have " + str(h) + " cards in your hand."
            print "You have to discard " + str(h - self.maxhand) + " cards."
            d = player.select_card(player.hand)
            while (d == None):
                print "Please make a selection."
                d = player.select_card(player.hand)
            player.discard_hand_card(d)
            h -= 1
        
    """
    * Communication round
    Players may play cards from their hands.
    (Players may deploy agents to friendly or enemy locations)
    Damage calculation for infiltrated agents 
    """
    def comm_phase(self,player):
        # Allow players to play cards, deploy agents etc.
        self.active_phase_menu(player)
        
        # Calculate communication damage
        other = self.find_other_player(player)
        for loc in other.locations:
            rounds = [] # List filled with the number of rounds each agent is infiltrated.  
            if (loc.attackers and loc.guards):
                print "Calculating damage for " + loc.name
                atkint = 0
                atkinfil = 0
                dmg = 0
                for a in loc.attackers:
                    print "Intelligence is " + str(a.int)                    
                    atkint += a.int
                    print "Infiltration is " + str(a.infil)
                    atkinfil += a.infil                    
                    rounds.append(a.rounds)
                for g in loc.guards:
                    dmg += self.calc_infoleak_dmg(g,atkint,atkinfil,rounds)
                print "Your agents in " + loc.name + " dealed " + str(dmg) + " to the opponent"
                other = self.find_other_player(player)
                other.bits -= dmg

        # Hostile agents in unguarded locations can now destroy the locations.
        for loc in other.locations:
            if (loc.destroyrounds == False):
                if (loc.attackers and not loc.guards):
                    print "Your agents in " + loc.name + " can now destroy the location."
                    answ = query_yes_no("Destroy location?", "yes")
                    if (answ == 'yes'):
                        loc.destroyrounds = 3
                        print "Location is to be destroyed in " + str(loc.destroyrounds) + " rounds."
                    else:
                        print "Alright, as you wish."   
                    
                
    """
    Formula atm is:
    dmg = ((atkint+atkinfil)*rounds)*(cipher/100)

    Vinegere = 5% reduction
    DES = 10% reduction
    3DES = 15% reduction
    TEA = 20% reduction
    XTEA = 25% reduction
    RC4 = 30% reduction
    Camellia = 35% reduction
    Blowfish = 40%
    Twofish = 50%
    AES-CTR 128 = 60%
    AES-ECB 128 = 70%
    AES-CBC 128 = 80%
    AES-CBC 256 = 95%
    """
    def calc_infoleak_dmg(self,guard,atkint,atkinfil,rounds):
        if (guard.cipher == "Vinegere"):
            cipher = 95
        elif (guard.cipher == "DES"):
            cipher = 90
        elif (guard.cipher == "3DES"):
            cipher = 85
        elif (guard.cipher == "TEA"):
            cipher = 80
        elif (guard.cipher == "XTEA"):
            cipher = 75
        elif (guard.cipher == "RC4"):
            cipher = 70
        elif (guard.cipher == "Camellia"):
            cipher = 65
        elif (guard.cipher == "Blowfish"):
            cipher = 60
        elif (guard.cipher == "Twofish"):
            cipher = 50
        elif (guard.cipher == "AES-CTR 128"):
            cipher = 40
        elif (guard.cipher == "AES-ECB 128"):
            cipher = 30
        elif (guard.cipher == "AES-CBC 128"):
            cipher = 20
        elif (guard.cipher == "AES-CBC 256"): # teh lulz
            cipher = 5

        dmg = atkint+atkinfil
        for r in rounds:
            dmg *= r
        dmg *= float(cipher)/100

        return int(dmg)
        
    def battle_phase(self,player):
        other = self.find_other_player(player)
        print "\n[B] Battle phase:"
        for loc in player.locations:
            if (loc.guards and loc.attackers):
                for a in loc.attackers:
                    if (a.found):
                        print "[B] Guard attacks."                    
                        print "[B] What should I do with " + a.title
                        print "[B] Starting physical battle!"
                        # TOFIX 'till I implement get_best_physical_guard()
                        g = random.choice(loc.guards)
                        if (self.battle(g,a)): # guard won
                            loc.attackers.remove(a)
                            other.graveyard.append(a)
                            print "[B] Intruder " + a.title + " defeated! :)"
                        else:
                            loc.guards.remove(g)
                            player.graveyard.append(g)
                            print "[B] Guard " + g.title + " defeated! :("
                            
        for rogue in other.rogues:
            print "[B] Rogue fights"
            print "[B] Rogue found: " + rogue.title
            answ = query_yes_no("[B] Attack?","yes")
            if (answ == "yes"):
                attacker = select_agent(player,False)
                if (attacker is False):
                    print "No available agents"
                    return False
                if (attacker is None):
                    print "No agent was selected"
                    return None
                if (self.battle(attacker,rogue)):
                    rogue.player.graveyard.append(rogue)
                    rogue.destroy()
                else:
                    print "[B] Agent failed to kill rogue agent."
                    attacker.player.active.remove(attacker)
                    attacker.player.graveyard.append(attacker)
                    attacker.destroy()
            else:
                print "Alright, as you wish!" 
            
    """
    Executes the battle between 'attacker' and 'defender'
    and cleans up the bodies afterwards
    """
    def battle(self,attacker,defender):
        if (self.physical_battle(attacker,defender)): # attacker won
            defender.destroy()
            return True
        else:
            attacker.destroy()
            return False
        
    def active_phase(self,player):
        print "\n[A] Active phase:"
        self.active_phase_menu(player)
        
        
    """
    Gives a menu for:
    Players may play cards from their hands.
    Players may deploy agents to friendly or enemy locations
    """
    def active_phase_menu(self,player):
        while 1:
            print "\nPlease enter your action: p/g/u/d/m/?"
            i = raw_input().lower()
            if (i == "p"):
                c = player.select_card(player.hand)
                if (c is None):
                    continue
                else:
                    if (self.play_card(player,c) == True):
                        # remove card from hand and put it into graveyard
                        player.discard_hand_card(c)
            elif (i == "g"):
                if (player.pawngenround == True):
                    print "You have already generated a pawn this round." 
                    continue
                if (player.areaslots < player.curareaslots + 1):
                    print "No slots in active area. Build more locations."
                    continue
                else: 
                    player.pawngenround = True
                    player.active.append(Agent(player))
                    break
            elif (i == "u"):
                agent = select_agent(player,False)            
                if (agent is False):
                    print "No available agents"
                    return False
                if (agent is None):
                    print "No agent was selected"
                    return None
            elif (i == "d"):
                self.deploy_agents_act(player)
            elif (i == "m"):
                game_menu(self,player)
            elif (i == "?"):
                print """
                p: play card
                g: generate pawn agent
                u: upgrade agent tier
                d: deploy agents
                ?: this menu
                Enter to proceed
                """
            elif (i ==""):
                break
            else:
                continue
        
    """
    Puts an agent to a friendly or enemy location.
    """
    def deploy_agents_act(self,player):
        while 1:
            print "Please enter your action: o/d/a/g/m/t/?"
            i = raw_input().lower()
            
            other = self.find_other_player(player)
            if (i == "o"): # offence
                agent = select_agent(player,False)            
                if (agent is False):
                    print "No available agents"
                    return False
                if (agent is None):
                    print "No agent was selected"
                    return None
                loc = select_enemy_card(other.locations)
                if (loc is None):
                    print "No location was selected"
                    return None
                elif (loc is False):
                    print "No locations on the enemy's field."
                    return False
                player.active.remove(agent)
                agent.travel(loc)
                break
            elif (i == "d"): # defence
                agent = select_agent(player,False)            
                if (agent is False):
                    print "No available agents"
                    return False
                if (agent is None):
                    print "No agent was selected"
                    return None
                loc = player.select_card(player.locations)
                if (loc is None):
                    print "No location was selected"
                    return None
                elif (loc is False):
                    print "No locations on your field."
                    return False
                player.active.remove(agent)
                agent.travel(loc)
                break
            elif (i == "a"): # move attacker
                agent = select_deployed_agent(self,player,True)
                if (agent is False):
                    print "No available agents"
                    return False
                if (agent is None):
                    print "No agent was selected"
                    return None
                agent.fallback(True)
                break
            elif (i == "g"): # move guard
                agent = select_deployed_agent(self,player,False)
                if (agent is False):
                    print "No available agents"
                    return False
                if (agent is None):
                    print "No agent was selected"
                    return None
                agent.fallback(True)
                break
            elif (i == "t"):
                agent = select_agent(player,False)
                if (agent is False):
                    print "No available agents"
                    return False
                if (agent is None):
                    print "No agent was selected"
                    return None
                if (agent.train() == False):
                    print "Already trained this turn."
                break
            elif (i == "m"):
                game_menu(self,player)
            elif (i == "?"):
                print """
                o: offencive deployment
                d: defencive deployment
                a: move attacker
                g: move guard
                t: train agent
                ?: this menu
                Enter to proceed
                """
            else:            
                break
            

    """            
    * Upkeep:
    Untap agents.
    Gain entropy.
    Upkeep effects.
    Player draws one card.
    Agent arrival.
    Stealth rolls.
    Collect rogue agents
    """
    def upkeep_phase(self,player):
        print "[U] Upkeep phase:"
        # Calculate entropy:
        self.gen_upkeep_entropy(player)
        
        # Upkeep effects

        # Necessary per-round housekeeping
        self.round_housekeeping(player)
        
        # Draw one card
        print "[U] Drawing card:\n"
        draw_cards_crypto(1,player.deck)
        dump_card(player.hand[0]) #dump the drawn card
        
        # Agent arrival
        self.agents_arrival(player)

        # Stealth rolls
        for loc in player.locations:
            if (loc.attackers and loc.guards):
                guardint = 0 # total int of guards
                for g in loc.guards:
                    guardint += g.int
                for a in loc.attackers:
                    if (self.stealth_check(a,guardint,loc)):
                        a.found = True
                        a.hidden = False
                        print a.title + " detected in " + loc.name + "!"

        for r in player.rogues:
            print "Rogue agent " + r.title + " found."
            if (player.areaslots >= player.curareaslots + r.slots):
                answ = query_yes_no("Put him in active area?", "yes")
                if (answ == "yes"):
                    player.rogues.remove(r)
                    r.fallback(True)
                    print r.title + " is now returning to the active area."
            else:
                print "No slots in active area. Can't collect rogue agent." 

    """
    * Increases agent.rounds
    """
    def round_housekeeping(self,player):
        other = self.find_other_player(player)
        
        # Resetting pawn generation tracker
        for p in self.players:
            if (p.pawngenround):
                p.pawngenround = False
                
        # Untap all agents
        for a in player.active:
            if (a.tapped):
                a.untap()
                
        # Increase the rounds inside a location for infiltrators.
        for loc in other.locations:
            if (loc.attackers):
                for a in loc.attackers:
                    a.rounds += 1

        # Resetting alreadytrained.
        for a in player.agents:
            if (a.alreadytrained):
                a.alreadytrained = False

        # Reduce destroyrounds of locations to be destroyed
        for loc in other.locations:
            if (loc.destroyrounds != False):
                if (loc.attackers and loc.destroyrounds != 0):
                    loc.destroyrounds -= 1
                    if (loc.destroyrounds != 0):
                        print "[U] Location " + loc.name + " is to be destroyed \
in " + str(loc.destroyrounds) + " rounds."
                else:
                    print "[U] No attackers in " + loc.name + ". Resetting destruction operation."
                    loc.destroyrounds = False
                if (loc.destroyrounds == 0):
                    print "[U] Location " + loc.name + " succesfully destroyed!"
                    loc.destroy()
        
    """
    This function iterates the player's 'travelling' list, and
    assigns the travelling agents to their 'goingto' locations.
    """
    def agents_arrival(self,player):
       for a in player.travelling:
           if (a.goingto == False):
               a.return_to_active_area()
               continue
           if (a.goingto == None):
               print a.title + "is travelling to None!!!!"
               continue
           if (a.goingto.player == a.player): # Friendly loc.
               a.goingto.guards.append(a)
               print "[U] " + a.title + " now guarding location: " + a.goingto.name
               a.finish_travel(a.goingto)
           else: # Enemy loc. Add to attackers.
               if a.goingto.discovered(a): # passed traceability test
                   a.goingto.attackers.append(a)
                   print "[U] Location " + a.goingto.name + " discovered. Agent attached."
                   # if guard is present in location: stealth check.
                   if (a.goingto.guards):
                       guardint = 0
                       for g in a.goingto.guards:
                           guardint += g.int
                       if (self.stealth_check(a,guardint,a.goingto)):
                           print "[U] " + a.title + "  was detected. Falling back"
                           a.hidden = False
                           a.fallback(True)
                           continue
                   a.finish_travel(a.goingto)
                   a.rounds = 1
               else:
                   print "[U] " + a.title + " couldn't discover location. Falling back." 
                   a.fallback(True)
               
    """
    This method is called when a 'card' is to be played by
    'player'. It calls the correct function for the card's type
    play_*_card() functions should return True when executed
    properly.
    """
    def play_card(self,player,card):
        # Entropy check
        if (player.entropy < card.cost):
            print "You can't play " + card.name + " not enough moneyz!"
            return False
        player.entropy -= card.cost
        
        if (card.type == 'technology'):
            return self.play_tech_card(player,card)
        elif (card.type == 'agent'):
            return self.play_agent_card(player,card)
        elif (card.type == 'location'):
            return self.play_location_card(player,card)
        elif (card.type == 'equipment'):
            return self.play_equipment_card(player,card)
        

    def play_location_card(self,player,loc):
        if (len(player.locations) < self.maxlocs):
            loc.play()
            return True
        else:
            print "Maximum location limit reached."
            return False

    def play_equipment_card(self,player,equip):
        agent = select_agent(player,True)
        if (agent is False):
            print "No available agents"
            return False
        if (agent is None):
            print "No agent was selected"
            return None
        equip.attach(agent)
        return True
        
    def play_tech_card(self,player,tech):
        player.tech.append(tech)
        return True

    def play_agent_card(self,player,card):
        print "Select active agent to be promoted."
        agent = select_agent(player,True)
        if (agent is None):
            return False
        if (agent is False):
            print "No active agents."
            print "Aborted agent selection."
            return False
        if (agent.upgrade(card) == True):
            print "Agent upgraded."
            return True

    def gen_upkeep_entropy(self,player):
        player.entropy += self.upkeepentropy
        print "[U] Total entropy: " + str(player.entropy)
        
    # Direct attack of agent to player.
    def direct_attack(self,agent,player):
        player.bits -= agent.int

    # Physical battle between two agents.
    # Return True if attacker wins.
    # TOFIX 
    def physical_battle(self,attacker,defender):
        if (attacker.attack > defender.defence):
            return True
        else:
            return False

    """
    'Guard' tries to detect infiltrator 'hidden' in a location 'loc',
    if successful this function returns True
    """
    def stealth_check(self,hidden,guardint,loc):
        if ((hidden.infil + hidden.int) < (loc.diff + guardint + hidden.rounds*10)): # TOFIX
            return True
        else:
            return False

def main():
    try: 
        g = Crypto()
    except KeyboardInterrupt:
        print
        print "Detected C-c. Terminating."
                   
    
if __name__ == "__main__":
        main()
