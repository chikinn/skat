"""Library of generic functions to make writing AI players easier.

Feel free to add to this file.  If a function is so specific that only one bot
will use it, however, then it doesn't belong here."""

from skat_classes import *

### BIDDING

def bid_incrementally(r, maxBid):
    """Slowly bid up to the desired max."""
    if r.currentBid < LEGAL_BIDS[0] or type(r.bidHistory[-1]) == bool:
        bidType = int
    else:
        bidType = bool

    if r.currentBid > maxBid:
        return False
    
    elif r.currentBid == maxBid:
        if bidType == int:
            return False

    if bidType == int:
        return next_legal_bid(r.currentBid)
    else: # Bool
        return True

### PLAYING

def count_certain_tricks(suitContents, null=False):
    """Count how many tricks can be guaranteed won (or lost, for null)."""
    unsuitedContents = [card[0] for card in suitContents]

    order = reversed(ORDER) # Sort suit with best cards first.
    if null:
        order = NULL_ORDER

    nWinners = 0 # For a null game, these are really "losers".
    for card in order:
        if card in unsuitedContents:
            nWinners += 1
        else:
            break

    # Consider the worst case: one opponent holds the rest of the suit.
    nGaps = len(order) - nWinners
    if nWinners >= nGaps:
        return len(suitContents) # Bleed then sweep -- but watch out for trump!
    else:
        return nWinners

### OTHER

def get_random(h, n=1):
    """Return a list of n cards from the hand."""
    flatHand = flatten(h.cards)
    return random.sample(flatHand, n)
