"""Library of generic functions to make writing AI players easier.

Feel free to add to this file.  If a function is so specific that only one bot
will use it, however, then it doesn't belong here."""

from skat_classes import *

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
