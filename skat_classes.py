import random

SUITS        = 'dshc'
ORDER        = '789qktaj'
NULL_ORDER   = '789tjqka'
N_PLAYERS    = 3
N_CARDS      = 30 # Excluding kitty
LEGAL_BIDS   = (18,20,22,23,24,27,30,33,35,36,40,44,45,46,48,50,54,55,59,60)
GAMES        = ('null', 'diamonds', 'spades', 'hearts', 'clubs', 'grand')
# See Round. game_value() for null game values.
BASE_VALUES  = {'diamonds':9, 'spades':10, 'hearts':11, 'clubs':12, 'grand':24}
POINTS       = {'7':0, '8':0, '9':0, 'q':3, 'k':4, 't':10, 'a':11, 'j':2}
TOTAL_POINTS = 120
EXTRAS       = ('reveals', 'calls three quarters', 'calls everything!')
UNCALLABLE_EXTRAS = ('takes three quarters', 'loses three quarters',
                     'takes everything!', 'loses everything!')

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
    hasHighTrump = 'jc' in heldTrumps

    for i in range(2, len(allTrumps) + 1): # Backward from top
        hasThisTrump = allTrumps[-i] in heldTrumps
        if hasThisTrump != hasHighTrump: # Breaks the streak
            break
    else:
        i += 1 # Has (or is missing!) a complete set of trump

    return i - 1

def game_value(declaration, roundOver, jackMultiplier=None):
    if declaration[0] == 'null':
        if 'no kitty' in declaration and 'reveals' in declaration:
            return 59
        if 'no kitty' in declaration:
            return 35
        if 'reveals' in declaration:
            return 46
        return 23

    mult = 1 + jackMultiplier

    for item in ('no kitty',) + EXTRAS + UNCALLABLE_EXTRAS:
        if item in declaration:
            mult += 1

    if not roundOver: # Assume declarer will hit her targets.
        if 'calls three quarters' in declaration:
            mult += 1 # Anticipating 'take three quarters'
        if 'calls everything!' in declaration:
            mult += 1 # Anticipating 'take everything'

    return BASE_VALUES[declaration[0]] * mult

def flatten(listOfLists):
    return sum(listOfLists, [])

def next_legal_bid(bid):
    bid += 1
    while bid not in LEGAL_BIDS:
        bid += 1
    return bid

def round_up(bid, gameType):
    while bid % BASE_VALUES[gameType] != 0:
        bid += 1
    return bid


class Round:
    def __init__(self, names, verbosity):
        # Convention: p0 plays first, p1 bids first, p2 deals
        self.h = [self.Hand(i, names[i]) for i in range(N_PLAYERS)]
        self.declaration = [] # First item wll be game type.

        self.bidHistory  = [] # List of bids, yeses, and nos
        self.playHistory = [] # List of two-character card strings

        self.currentBid   = LEGAL_BIDS[0] - 1
        self.currentTrick = []

        self.cardsDeclarerTook  = []
        self.cardsDefendersTook = []
        
        self.verbosity = verbosity
        self.zazz = ['[BIDS]  ', '[HANDS] ', '[TRICKS]']

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

    def give_kitty(self):
        self.h[self.declarer].add(self.kitty)

    def check_overbid(self):
        hand = self.h[self.declarer]
        declaration = self.declaration
        gameType = declaration[0]

        if self.verbosity == 'verbose':
            print('{} calls {}'\
                  .format(self.h[self.declarer].name, ', '.join(declaration)))

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
            if self.verbosity == 'verbose':
                self.h[i].show(self.zazz[1])
                self.zazz[1] = ' ' * len(self.zazz[1])

        handTrumps = hand.cards[-1]
        kittyTrumps = []
        for card in self.kitty:
            if card[0] == 'j' or card[1] == gameType[0]:
                kittyTrumps.append(card)
        heldTrumps = handTrumps + kittyTrumps
        self.jackMultiplier = jack_multiplier(heldTrumps, gameType)

        gameValue = game_value(declaration, False, self.jackMultiplier)
        if self.currentBid > gameValue:
            if self.verbosity == 'verbose':
                print('Overbid!')
            return round_up(self.currentBid, gameType)
        else:
            return False

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
                order = NULL_ORDER
            else:
                order = ORDER

            allTrumps = all_trumps(gameType)
            trumped = False
            for card in trick:
                if card in allTrumps:
                    trumped = True

            strength = -1
            for card in trick:
                if trumped:
                    if card not in allTrumps:
                        continue
                    strength = allTrumps.index(card)
                else:
                    if card[1] == suitLed:
                        strength = order.index(card[0])

                if strength > highCardStrength:
                    highCard, highCardStrength = card, strength

            trickWinner = (whoseTurn + trick.index(highCard) + 1) % N_PLAYERS
            if trickWinner == self.declarer:
                self.cardsDeclarerTook += trick
            else:
                self.cardsDefendersTook += trick

            if self.verbosity == 'verbose':
                print(self.zazz[2], '{} leads {} {} {} --> {}'
                      .format(self.h[(whoseTurn + 1) % N_PLAYERS].name,
                              trick[0], trick[1], trick[2],
                              self.h[trickWinner].name))
                self.zazz[2] = ' ' * len(self.zazz[2])

            self.currentTrick = []
            self.whoseTurn = trickWinner

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

    def score(self):
        points = sum([POINTS[card[0]] for card in self.cardsDeclarerTook])

        if points >= TOTAL_POINTS * 3/4:
            self.declaration.append('takes three quarters')
        elif points <= TOTAL_POINTS * 1/4:
            self.declaration.append('loses three quarters')

        if self.cardsDefendersTook == []:
            self.declaration.append('takes everything!')
        elif self.cardsDeclarerTook == []:
            self.declaration.append('loses everything!')

        d = self.declaration
        gameValue = game_value(d, True, self.jackMultiplier)
        if d[0] == 'null':
            won = 'lost everything' in d
        else: # Suit or grand game
            overbid = ('calls three quarters' in d and \
                       'takes three quarters' not in d) \
                      or \
                      ('calls everything!' in d and \
                       'takes everything!' not in d)
            won = points > TOTAL_POINTS / 2 and not overbid

        if won:
            out = gameValue
        else:
            if d[0] != 'null' and overbid:
                gameValue = round_up(self.currentBid, d[0])
            out = -2 * gameValue

        if self.verbosity == 'verbose':
            if len(d) > 1:
                print(', '.join(d[1:]))
            if overbid:
                print('Overbid!')
            print('{} scores {}'.format(self.h[self.declarer].name, out))
        elif self.verbosity == 'scores':
            print('{} {}'.format(self.h[self.declarer].name, out))

        return out

    def get_bid(self, p, i):
        bid = p.bid(self.h[i], self)
        if self.verbosity == 'verbose':
            print(self.zazz[0], '{} bids {}'.format(self.h[i].name, bid))
            self.zazz[0] = ' ' * len(self.zazz[0])
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
            if self.verbosity == 'verbose':
                print('skips the kitty!')
        self.declarer = i
        self.whoseTurn = i
        return declaration

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
                assert item == 'no kitty' or item == 'reveals'

        # In non-null games, calling extras requires skipping the kitty.
        elif 'no kitty' not in declaration:
            assert len(declaration) == 1
    
    def get_play(self, p):
        hand = self.h[self.whoseTurn]
        cardToPlay = p.play(hand, self)
        
        hand.drop(cardToPlay)
        self.playHistory.append(cardToPlay)
        self.currentTrick.append(cardToPlay)


    class Hand:
        def __init__(self, i, name):
            self.cards = [[], [], [], [], []] # D, S, H, C, trump
            self.seat = i # 0, 1, or 2
            self.name = name

        def show(self, zazz):
            out = []
            for suit in self.cards:
                out.append(' '.join(suit))
            print(zazz, self.name + ':', ' | '.join(out))

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

# graphics class (later) -- display outside of a console window
