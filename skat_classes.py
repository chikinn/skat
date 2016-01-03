import random

SUITS        = 'dshc'
ORDER        = '789qktaj'
NULL_ORDER   = '789tjqka'
N_PLAYERS    = 3
N_CARDS      = 30 # Excluding kitty
MIN_BID      = 18
GAMES        = ('null', 'diamonds', 'spades', 'hearts', 'clubs', 'grand')
# See Round. game_value() for null game values.
BASE_VALUES  = {'diamonds':9, 'spades':10, 'hearts':11, 'clubs':12, 'grand':24}
EXTRAS       = ('reveal', 'call three quarters', 'call everything')
POINTS       = {'7':0, '8':0, '9':0, 'q':3, 'k':4, 't':10, 'a':11, 'j':2}
TOTAL_POINTS = 120

def all_trumps(gameType):
    allTrumps = [] # For a null game, this will be returned unmodified.
    if gameType != 'null':
        if gameType != 'grand':
            allTrumps += [val + gameType[0] for val in ORDER[:-1]] 
        allTrumps += ['j' + suit for suit in SUITS]
    return allTrumps

def jack_multiplier(heldTrumps, gameType):
    # heldTrumps is a list of all trump in the hand and kitty.
    assert gameType in GAMES
    if gameType == 'null':
        return None

    allTrumps = all_trumps(gameType)

    if 'jc' in heldTrumps:
        for i in range(2, len(allTrumps) + 1): # Backward from top
            if allTrumps[-i] not in heldTrumps:
                break 
            i += 1 # TODO: clean up
    else:
        for i in range(2, len(allTrumps) + 1):
            if allTrumps[-i] in heldTrumps:
                break
            i += 1
    
    return i - 1

def game_value(declaration, roundOver, jackMultiplier=None):
    if declaration[0] == 'null':
        if 'no kitty' in declaration and 'reveal' in declaration:
            return 59
        if 'no kitty' in declaration:
            return 35
        if 'reveal' in declaration:
            return 46
        return 23

    mult = 1 + jackMultiplier

    for item in EXTRAS + ('no kitty', 'take three quarters', \
                          'take everything', 'lose three quarters', \
                          'lose everything'):
        if item in declaration:
            mult += 1

    if not roundOver: # Assume declarer will hit her targets.
        if 'call three quarters' in declaration:
            mult += 1 # Anticipating 'take three quarters'
        if 'call everything' in declaration:
            mult += 1 # Anticipating 'take everything'

    return BASE_VALUES[declaration[0]] * mult

def flatten(listOfLists):
    return sum(listOfLists, [])

class Round:
    def __init__(self):
        # Convention: p0 plays first, p1 bids first, p2 deals
        self.h = [self.Hand(i) for i in range(N_PLAYERS)]
        self.declaration = [] # First item wll be game type.

        self.bidHistory  = [] # List of bids, yeses, and nos
        self.playHistory = [] # List of two-character card strings

        self.currentBid   = MIN_BID - 1
        self.currentTrick = []

        self.cardsDeclarerTook  = []
        self.cardsDefendersTook = []

    def generate_deck(self):
        # Construct an unshuffled deck.
        deck = []
        for suit in SUITS:
            for value in ORDER:
                deck.append(value + suit)

        self.cardsLeft = deck # Start keeping track of unplayed cards.

        random.shuffle(deck)
        
        self.h[0].add(deck[:10])   # Deal to hands ...
        self.h[1].add(deck[10:20]) #
        self.h[2].add(deck[20:30]) #
        self.kitty = deck[30:]     # ... and to kitty.

    def get_bid(self, p, i):
        bid = p.bid(self.h[i], self)
        #print('Seat {} bids {} (history: {})'.format(i, bid, self.bidHistory))
        if len(self.bidHistory) > 0 and type(self.bidHistory[-1]) is int:
            assert type(bid) is bool # Adjacent bids are never numbers.
        elif type(bid) is int:
            assert bid > self.currentBid # Numeric bids must be raises.
            self.currentBid = bid

        self.bidHistory.append(bid)
        return bid

    def get_kitty_declaration(self, p, i):
        declaration = p.kitty(self.h[i].cards, self)
        assert type(declaration) is bool

        if not declaration:
            self.declaration.append('no kitty')
        self.declarer = i
        self.whoseTurn = i
        return declaration

    def give_kitty(self):
        self.h[self.declarer].add(self.kitty)

    def get_kitty_discards(self, p):
        hand = self.h[self.declarer]
        discards = p.discard(hand, self)
        assert len(discards) == len(discards[0]) == len(discards[1]) == 2

        self.kitty = []
        for discard in discards:
            hand.drop(discard)
            self.kitty.append(discard)

    def get_declaration(self, p):
        declaration = p.declare(self.h[self.declarer], self)

        assert declaration[0] in GAMES
        self.declaration.insert(0, declaration[0])

        for item in declaration[1:]:
            assert item in EXTRAS
            self.declaration.append(item)

        # Only certain extras may be called in a null game.
        if self.declaration[0] == 'null':
            for item in declaration[1:]:
                assert item == 'no kitty' or item == 'reveal'

        # In non-null games, calling extras requires skipping the kitty.
        elif 'no kitty' not in declaration:
            assert len(declaration) == 1
    
    def check_overbid(self):
        hand = self.h[self.declarer]
        declaration = self.declaration
        gameType = declaration[0]

        #
        # Overbidding a null game should never happen since the kitty, points
        # taken, and tricks taken don't affect the multiplier.  My arbitrary
        # way to handle it is to keep the bid as the penalty.
        #
        if gameType == 'null':
            self.jackMultiplier = None
            gameValue = game_value(declaration, False)
            if self.currentBid > gameValue:
                return gameValue
            else:
                return False

        for i in range(N_PLAYERS):
            self.h[i].reorganize(gameType) # Reorganize everyone's hands.
            self.h[i].show()

        handTrumps = hand.cards[-1]
        kittyTrumps = []
        for card in self.kitty:
            if card[0] == 'j' or card[1] == gameType[0]:
                kittyTrumps.append(card)
        heldTrumps = handTrumps + kittyTrumps
        self.jackMultiplier = jack_multiplier(heldTrumps, gameType)

        gameValue = game_value(declaration, False, self.jackMultiplier)
        if self.currentBid > gameValue:
            while self.currentBid % BASE_VALUES[gameType] != 0:
                self.currentBid += 1
        else:
            return False

    def get_play(self, p):
        hand = self.h[self.whoseTurn]
        cardToPlay = p.play(hand, self)
        
        hand.drop(cardToPlay)
        self.playHistory.append(cardToPlay)
        self.currentTrick.append(cardToPlay)

    def next_turn(self):
        whoseTurn = self.whoseTurn
        gameType = self.declaration[0]
        trick = self.currentTrick

        if len(trick) < 3: # Trick is not finished yet.
            self.whoseTurn = (whoseTurn + 1) % N_PLAYERS

        else: # Award trick to whoever played the strongest card.
            highCardStrength = -1
            suitLed = trick[0][1]

            if gameType == 'null':
                for card in trick:
                    strength = NULL_ORDER.index(card[0])
                    suit = card[1]
                    if suit == suitLed and strength > highCardStrength:
                        highCard, highCardStrength = card, strength

            else: # Not a null game
                trumped = False
                for card in trick:
                    if card[0] == 'j' or card[1] == gameType[0]:
                        trumped = True

                if trumped:
                    allTrumps = all_trumps(gameType)
                    for card in trick:
                        if card in allTrumps:
                            strength = allTrumps.index(card)
                            if strength > highCardStrength:
                                highCard, highCardStrength = card, strength

                else: # No trump in this trick # TODO: clean up repetition
                    for card in trick:
                        strength = ORDER.index(card[0])
                        suit = card[1]
                        if suit == suitLed and strength > highCardStrength:
                            highCard, highCardStrength = card, strength

            trickWinner = (whoseTurn + trick.index(highCard) + 1) % N_PLAYERS
            if trickWinner == self.declarer:
                self.cardsDeclarerTook += trick
            else:
                self.cardsDefendersTook += trick

            self.currentTrick = []
            self.whoseTurn = trickWinner

    def score(self): # TODO: implement overbids properly
        points = sum([POINTS[card[0]] for card in self.cardsDeclarerTook])

        if points >= TOTAL_POINTS * 3/4:
            self.declaration.append('took three quarters')
        elif points <= TOTAL_POINTS * 1/4:
            self.declaration.append('lost three quarters')

        if self.cardsDefendersTook == []:
            self.declaration.append('took everything')
        elif self.cardsDeclarerTook == []:
            self.declaration.append('lost everything')

        d = self.declaration
        gameValue = game_value(d, True, self.jackMultiplier)
        if d[0] == 'null':
            won = 'lost everything' in d
        else: # Suit or grand game
            overcalled = ('called three quarters' in d and \
                          'took three quarters' not in d) \
                         or \
                         ('called everything' in d and \
                          'took everything' not in d)
            won = points > TOTAL_POINTS / 2 and not overcalled

        if won:
            return gameValue
        else:
            return -2 * gameValue

    def legal_plays(self, hand):
        if len(self.currentTrick) == 0:
            return flatten(hand.cards)

        cardLed = self.currentTrick[0]
        if cardLed in all_trumps(self.declaration[0]):
            legalPlays = hand.cards[-1]
        else:
            legalPlays = hand.cards[SUITS.find(cardLed[1])]

        if legalPlays == []: # Can't follow suit
            return flatten(hand.cards) # May play any card
        else:
            return legalPlays

    class Hand:
        def __init__(self, i):
            self.cards = [[], [], [], [], []] # D, S, H, C, trump
            self.seat = i # 0, 1, or 2

        def show(self):
            print(self.cards)

        def add(self, newCards):
            self.cards[-1] += newCards # Add to end of hand arbitrarily.

        def drop(self, card):
            for suit in self.cards:
                if card in suit:
                    suit.remove(card)
                    break

        def reorganize(self, gameType):
            if gameType == None: # No organization needed
                return

            # Undesignate suits, preparing to redistribute.
            newCards = [card for suit in self.cards for card in suit]
            self.cards = [[], [], [], [], []]

            if gameType == 'grand':
                for card in newCards:
                    if card[0] == 'j':
                        self.cards[4].append(card)
                    else:
                        self.cards[SUITS.find(card[1])].append(card)
                def sortKey(card):
                    return 10 * SUITS.find(card[1]) + ORDER.find(card[0])

            elif gameType == 'null':
                for card in newCards:
                    self.cards[SUITS.find(card[1])].append(card)
                order = NULL_ORDER
                def sortKey(card):
                    return 10 * SUITS.find(card[1]) + NULL_ORDER.find(card[0])

            else:                 # Suit game (four possible types)
                for card in newCards:
                    if card[0] == 'j' or card[1] == gameType[0]:
                        self.cards[4].append(card)
                    else:
                        self.cards[SUITS.find(card[1])].append(card)
                def sortKey(card):
                    key = 10 * SUITS.find(card[1]) + ORDER.find(card[0])
                    if card[0] == 'j':
                        key += 100 # Make sure jacks sort above other trump.
                    return key

            # Now that the cards are in the correct suits, sort each suit.
            self.cards = [sorted(suit, key=sortKey) for suit in self.cards]

# <wrapper> -- play many games, keep score, rotate starting player/seating
# round class argument: print (none/minimal/verbose)
# graphics class (later) -- display outside of a console window
