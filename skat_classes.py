"""Low-level classes and functions for tracking state of a skat round.

Intended to be imported by a higher-level game manager (play_skat).  The meat
of this file is the Round class, which stores the information visible to all
players (and more), along with the nested Hand class, which stores player-
specific information.

Some methods and especially the top-level functions may be useful in building
AI players.

Common attributes/arguments:
  bid (int/bool): a bid (int > 17) or indication of OK (True) or pass (false).
  card (str): Two-character representation of a standard playing card, a value
    (see ORDER) followed by a suit (see SUITS).  E.g. 'jc', jack of clubs.
  declaration (list of str): First item is always gameType.  Other items are
    bonuses called during the bidding or earned during the trick taking that
    affect the game value multiplier (see EXTRAS, UNCALLABLE_EXTRAS).
  gameType (str): Game chosen by declarer ('null', a suit, or 'grand' -- see
    GAMES).  Always the first item in a declaration.
  names (list of str): How to identify the players in printed output.
"""

import random

SUITS        = 'dshc'
ORDER        = '789qktaj'
NULL_ORDER   = '789tjqka'
N_PLAYERS    = 3
N_CARDS      = 30 # Excluding kitty
LEGAL_BIDS   = (18,20,22,23,24,27,30,33,35,36,40,44,45,46,48,50,54,55,59,60)
GAMES        = ('null', 'diamonds', 'spades', 'hearts', 'clubs', 'grand')
# See game_value() for null game values.
BASE_VALUES  = {'diamonds':9, 'spades':10, 'hearts':11, 'clubs':12, 'grand':24}
POINTS       = {'7':0, '8':0, '9':0, 'q':3, 'k':4, 't':10, 'a':11, 'j':2}
TOTAL_POINTS = 120
EXTRAS       = ('reveals', 'calls three quarters', 'calls everything!')
UNCALLABLE_EXTRAS = ('takes three quarters', 'loses three quarters',
                     'takes everything!', 'loses everything!')

def all_trumps(gameType):
    """Return the entire trump suit (list of str) for the given gameType."""
    allTrumps = [] # For a null game, this will be returned unmodified.
    if gameType != 'null':
        if gameType != 'grand':
            allTrumps += [val + gameType[0] for val in ORDER[:-1]] 
        allTrumps += ['j' + suit for suit in SUITS]
    return allTrumps

def jack_multiplier(heldTrumps, gameType):
    """Return the jack multiplier (0 < int < 12), for calculating game value.
    
    heldTrumps (list of str): Combined trump in kitty and declarer's hand.
    """
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
    """Return the game value (int), typically a base value times a multiplier.
    
    roundOver (bool): Whether trick taking has concluded.
    jackMultiplier (0 < int < 12): See jack_multiplier().
    """
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
    """Return the entries of the input's sublists (list)."""
    return sum(listOfLists, []) # No idea why this works

def next_legal_bid(bid):
    """Return the lowest bid (int > 0)that may be made after the given bid."""
    bid += 1
    while bid not in LEGAL_BIDS:
        bid += 1
    return bid

def round_up_overbid(bid, gameType):
    """For an overbid, return next multiple (int > 0) of game's base value."""
    if self.verbosity == 'verbose':
        print('Overbid!')
    while bid % BASE_VALUES[gameType] != 0:
        bid += 1
    return bid


class Round:
    """Store round info and interact with AI players.

    Attributes (see below) mainly correspond to public knowledge.  The nested
    Hand class, however, stores private, player-specific info.  Thus there is
    one Hand per player.

    Methods whose names begin with 'get_' retrieve a move from an AI player
    object on their turn.  Taken together these specify all the methods needed
    for a complete AI class.

    bidHistory (list of int/bool): Chronological bids so far (incl. OK/pass).
    cardsDeclarerTook (list of str): Cards taken so far by the declarer.
    cardsDefendersTook (list of str): Ditto for the other team.
    cardsLeft (list of str): Cards that not all players have seen yet.
    currentBid (int): Highest bid so far (ignoring OK/pass).
    currentTrick (list of str): The 0-3 cards played so far this trick. 
    declaration (list of str): See module-level docstring.
    h (list of obj): One Hand per player.  NOT public info.
    jackMultiplier (0 < int < 12): See jack_multiplier().
    kitty (list of str): Two cards, either for declarer to pick up or already
      discarded by her.  NOT public info.
    playHistory (list of str): Chronological cards played so far.
    verbosity (str): How much to show ('silent', 'scores', or 'verbose').
    zazz (list of str): Schnazzy labeled indents for verbose output.
    """

    def __init__(self, names, verbosity):
        """Instantiate a Round and its three Hand sub-objects."""
        self.h = [self.Hand(i, names[i]) for i in range(N_PLAYERS)]
        self.declaration = []

        self.bidHistory  = []
        self.playHistory = []

        self.currentBid   = LEGAL_BIDS[0] - 1 # Initialize to below min bid.
        self.currentTrick = []

        self.cardsDeclarerTook  = []
        self.cardsDefendersTook = []
        
        self.verbosity = verbosity
        self.zazz = ['[BIDS]  ', '[HANDS] ', '[TRICKS]']

    def generate_deck(self):
        """Construct a deck, shuffle, and deal."""
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
        """Add cards from kitty to declarer's hand."""
        self.h[self.declarer].add(self.kitty)

    def check_overbid(self):
        """If bid (int) too high, round up and return, otherwise return False.

        There are two ways to overbid:
        (1) Right after declaring.  Either the kitty sabotages the declarer by
            including (or not including) a streak-altering trump, or the
            declarer miscalculated game value during the bidding.
        (2) During trick taking.  The declarer fails to meet a bonus criterion
            she was depending on to raise the game value.

        This method checks only the first way.  The second is checked during
        end-of-round scoring (see Round.score()).
        
        Also calculates and stores jackMultiplier, which is invariant
        throughout the round but becomes harder to calculate once cards have
        been played.
        """
        hand = self.h[self.declarer]
        declaration = self.declaration
        gameType = declaration[0]

        if self.verbosity == 'verbose':
            print('{} calls {}'\
                  .format(self.h[self.declarer].name, ', '.join(declaration)))

        #
        # Overbidding a null game should never happen since the kitty, points
        # taken, and tricks taken don't affect the multiplier.
        #
        if gameType == 'null':
            self.jackMultiplier = None # Is this line needed?
            gameValue = game_value(declaration, False)
            assert self.currentBid <= gameValue
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
            return round_up_overbid(self.currentBid, gameType)
        return False

    def next_turn(self):
        """Figure out whose turn is next and do various book-keeping."""
        whoseTurn = self.whoseTurn
        gameType = self.declaration[0]
        trick = self.currentTrick

        if len(trick) < 3: # Trick is not finished yet; continue clockwise.
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
        """Return legal plays (list) from this hand for the current trick."""
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
        """Add up cards to see if declarer won.  Return her score (int)."""
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
            won = 'loses everything!' in d
        else: # Suit or grand game
            overcalled = ('calls three quarters' in d and \
                          'takes three quarters' not in d) \
                         or \
                         ('calls everything!' in d and \
                          'takes everything!' not in d)
            won = points > TOTAL_POINTS / 2 and not overcalled

        if won:
            out = gameValue
        else:
            if self.currentBid > gameValue:
                gameValue = round_up_overbid(self.currentBid, d[0])
            out = -2 * gameValue

        if self.verbosity == 'verbose':
            if len(d) > 1:
                print(', '.join(d[1:]))
            print('{} scores {}'.format(self.h[self.declarer].name, out))
        elif self.verbosity == 'scores':
            print('{} {}'.format(self.h[self.declarer].name, out))

        return out

    def get_bid(self, p, i):
        """Return AI p's bid (int/bool) for seat i."""
        bid = p.bid(self.h[i], self)
        if self.verbosity == 'verbose':
            print(self.zazz[0], '{} bids {}'.format(self.h[i].name, bid))
            self.zazz[0] = ' ' * len(self.zazz[0])
        if len(self.bidHistory) > 0 and type(self.bidHistory[-1]) is int:
            assert type(bid) is bool # Can't have two numeric bids in a row.
        elif type(bid) is int:
            assert bid > self.currentBid # Numeric bids must be raises.
            self.currentBid = bid

        self.bidHistory.append(bid)
        return bid

    def get_kitty_declaration(self, p, i):
        """Return AI p's decision whether to take kitty (bool) for seat i."""
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
        """Return AI p's kitty discards (list of str) for declarer."""
        hand = self.h[self.declarer]
        discards = p.discard(hand, self)
        assert len(discards) == len(discards[0]) == len(discards[1]) == 2

        self.kitty = []
        for discard in discards:
            hand.drop(discard)
            self.kitty.append(discard)

    def get_declaration(self, p):
        """Return AI p's declaration (list of str)."""
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
        """Return AI p's play (str) for whoever's turn it is."""
        hand = self.h[self.whoseTurn]
        cardToPlay = p.play(hand, self)
        
        hand.drop(cardToPlay)
        self.cardsLeft.remove(cardToPlay)
        self.playHistory.append(cardToPlay)
        self.currentTrick.append(cardToPlay)


    class Hand:
        """Manage one player's hand of cards.

        cards (list of lists): One sublist per suit, in the order diamonds,
          spades, hearts, clubs, trump.  Note that in a null or suit game, one
          suit will always be empty.
        seat (int): Player ID number (0, 1, or 2).
        """

        def __init__(self, seat, name):
            """Instantiate a Hand."""
            self.cards = [[], [], [], [], []] # D, S, H, C, trump
            self.seat = seat 
            self.name = name

        def show(self, zazz):
            """Print cards (verbose output only)."""
            out = []
            for suit in self.cards:
                out.append(' '.join(suit))
            print(zazz, self.name + ':', ' | '.join(out))

        def add(self, newCards):
            """Add a list of cards to the hand without sorting."""
            self.cards[-1] += newCards # Add to trump suit arbitrarily.

        def drop(self, card):
            """Discard a card from the hand."""
            for suit in self.cards:
                if card in suit:
                    suit.remove(card)
                    break

        def reorganize(self, gameType):
            """Move all cards to the correct suit and sort within each suit."""
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
