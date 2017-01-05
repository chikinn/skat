""" Meet Donald the best player who only plays trump games

Donald will never bid a null game. He only bids if he has at least 4
of the Aces and Jacks. He then bids a Grand game if he has the top two
Jacks. If he does not have the top two jacks then he bids the game with
his longest suit. Ties are broken by suit without an ace. The winner of
the game will always bleed trump and the other players will always lead
their longest suit. If they have the winner play that otherwise they play
their lowest.
"""

from skat_classes import *
from bot_utils import *

class DonaldPlayer:

def assess_hand(self, h): #Returns a number to bid up to
	flat = h.flatten()
	count = 0
	for i in range(0, 9): #Counts # of Jacks and Aces
		h[x][0] == 'a':
			count++
	if count > 3: # needs at least 4 Jacks and Aces
		suit = largest_suit(h)
		if jack_multiplier(h[4],'grand') >2: #fix works for bottom jacks
			return game_value('grand',False,jack_multiplier(h[4],'grand'))
		else
			return game_value(suit,false,jack_multiplier(h[4],suit))

def bid(self, h):
	bid_incrementally(assess_hand(h))

def kitty(self, h, r):
	return True

def discard(self,h,r):
	





		





	def bid(self, h, r):


