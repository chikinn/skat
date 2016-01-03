from skat_classes import *

LEGAL_BIDS = (18,20,22,23,24,27,30,33,35,36,40,44,45,46,48,50,54,55,59,60)

def next_legal_bid(bid):
    bid += 1
    while bid not in LEGAL_BIDS:
        bid += 1
    return bid

class KennyPlayer:
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

        if h.seat == 1 and len(r.bidHistory)%2 == 0:
            # 50% chance of bidding higher (Player 1 first bidding phase)
            if stillBid:
                return next_legal_bid(r.currentBid)
            return False

        # Returns True or False (Player 1 if he wins first bidding phase)
        if h.seat == 1 and len(r.bidHistory)%2 == 1:
            return bool(random.getrandbits(1))  

        # 50% chance to bid higher (Player 2 only bids second round)
        if h.seat == 2:
            if stillBid:
                return next_legal_bid(r.currentBid)
            return False

    def get_random(self,h):
        if type(h.cards[0]) == list:
            flat = sum(h.cards,[])
        else:
            flat = h.cards
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
        return [random.choice(GAMES)]

    def play(self, h, r):
        return random.choice(r.legal_plays(h))
