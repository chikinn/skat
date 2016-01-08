"""A random skat player.

Kenny always chooses a random card to play.  In the bidding, half the time he
passes and half the time he makes the (lowest) next legal bid.  When declaring,
he picks a game uniformly at random (and thus is biased toward suit games,
of which there are four compared to just one null option and one grand option),
always takes the kitty, and never calls any extras.

See play_skat and the Round class in skat_classes for context.
"""
from skat_classes import *

class KennyPlayer:
    def get_random(self,h):
        if type(h.cards[0]) == list:
            flat = sum(h.cards,[])
        else:
            flat = h.cards
        return random.choice(flat)

    def bid(self, h, r):
        stillBid  = bool(random.getrandbits(1)) 

        if h.seat == 0:
            if r.bidHistory == [False, False]:
                if stillBid:
                    return LEGAL_BIDS[0]
                else:
                    return False
            # Returns True or False (Player 0 always bids this way)
            return bool(random.getrandbits(1))

        if h.seat == 1 and len(r.bidHistory) % 2 == 0:
            # 50% chance of bidding higher (Player 1 first bidding phase)
            if stillBid:
                return next_legal_bid(r.currentBid)
            return False

        # Returns True or False (Player 1 if he wins first bidding phase)
        if h.seat == 1 and len(r.bidHistory) % 2 == 1:
            return bool(random.getrandbits(1))  

        # 50% chance to bid higher (Player 2 only bids second round)
        if h.seat == 2:
            if stillBid:
                return next_legal_bid(r.currentBid)
            return False

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
        return [random.choice(GAMES)]

    def play(self, h, r):
        return random.choice(r.legal_plays(h))
