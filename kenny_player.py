from skat_classes import *
import random

GAMES =      ('null', 'diamonds', 'spades', 'hearts', 'clubs', 'grand')
LEGAL_BIDS = (18,20,22,23,24,27,30,33,35,36,40,44,45,46,48,50,54,55,59,60)

class KennyPlayer:
    def bid(self, h, r):
         stillBid   =  bool(random.getrandbits(1)) 
         stillbid2  =  bool(random.getrandbits(1))
         i          =  0	                                #keeps track of legal bids

         if h.seat == p0:
             return bool(random.getrandbits(1))	        #Returns True or False (Player 0 always bids this way)
         if h.seat == p1 and len(r.bidHistory== 0):			
             while stillBid == True:                      #50% chance of bidding higher (Player 1 first bidding phase)
                 return LEGAL_BIDS[i]
                 i+=1
             return stillBid
         if h.seat == p1 and len(r.bidHistory)%2 == 0:   #Returns True or False (Player 1 if he wins first bidding phase
             return bool(random.getrandbits(1))  

        
         if h.seat == p2:                                #50% chance to bid higher (player 2 only bids second round)
             while stillBid2 == True:
                 return LEGAL_BIDS[i]
                 i+=1
                 return stillBid2    


    def get_random(self,h):
         if type(h[0]) == list:
             flat = sum(h,[])
         else:
             flat = h
         return random.choice(flat)


    def kitty(self, h, r):
         return True

    def discard(self, h, r):
         kitty1 = 0
         kitty2 = 0
         while kitty1 == kitty2:
             kitty1 = self.get_random(h)
             kitty2 = self.get_random(h)
         return [kitty1,kitty2]
 
    def declare(self, h, r):
         return random.choice(GAMES)
	
    def is_playable(self, h, r):
         pass 


    def play(self, h, r):
         pass

k = KennyPlayer()
#print(k.discard([["dk","dt","da"],["s7","s9"]],["c7","c8","c9","cq"]))
print(k.declare(1,2))


