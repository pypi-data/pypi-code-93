""" Bid for Game
    Board class
"""

from datetime import datetime
import json

from .player import Player
from .hand import Hand
from bridgeobjects import Board, RANKS, SEATS, parse_pbn, Contract, Auction, Trick, Card


class Auction(Auction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def to_json(self):
        """Return object as json string property."""
        calls = [call.name for call in self.calls]
        json_str = json.dumps(calls)
        return json_str


class Contract(Contract):
    def __init__(self, name='', declarer='', auction=None):
        super().__init__(name, declarer, auction)

    @property
    def to_json(self):
        """Return object as json string property."""
        json_str = json.dumps({
            'name': self.name,
            'declarer': self.declarer,
        })
        return json_str


class Trick(Trick):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def to_json(self):
        """Return object as json string property."""
        json_str = json.dumps({
            'cards': [card.name for card in self.cards],
            'leader': self.leader,
            'note_keys': self.note_keys,
            'winner': self.winner,
        })
        return json_str

    def from_json(self, json_str):
        """Populate the attributes from the json string."""
        trick_dict = json.loads(json_str)
        self.cards = [Card(name) for name in trick_dict['cards']]
        self.leader = trick_dict['leader']
        self.winner = trick_dict['winner']
        return self


class Board(Board):
    """Define BfG Board class."""
    SEAT_SEATS = ['N', 'E', 'W', 'S', 'Random']
    SLAM_POINTS = 32
    STATUS = {
        0: 'OK',
        1: 'JSONDecodeError',
        2: 'File not found',
        3: 'Type error',
        99: 'Unknown error',
        'OK': 0,
        'JSONDecodeError': 1,
        'File not found': 2,
        'Type error': 3,
        'Unknown error': 99,
    }
    PLAY_STATUS = {
        0: 'no change',
        1: 'card played',
        2: 'previous trick',
        3: 'replay board',
        'no change': 0,
        'card played': 1,
        'previous trick': 2,
        'replay board': 3,
    }

    def __init__(self, *args, **kwargs):
        super(Board, self).__init__(*args, **kwargs)
        self.auction = Auction()
        self.description = ''
        self.bid_history = []
        self.active_bid_history = []
        self._stage = None
        self.players = {}
        for index in range(4):
            self.players[index] = Player(self, None, index)
        self.check_bids = []
        self._dealer = None
        self.leader = None
        self.current_player = None
        self.current_trick = Trick()
        self.reset = False
        self._dict = {}
        self._status = self.STATUS['OK']
        self.play_status = self.PLAY_STATUS['no change']
        self.play_master = ''

    def __repr__(self):
        """Return a string representation of the deal."""
        return f"Board: North's hand {self.hands[0]}"

    def __str__(self):
        """Return a string representation of the deal."""
        return f"Board: North's hand {self.hands[0]}"

    @property
    def status(self):
        """Return the board's status."""
        return self._status

    @status.setter
    def status(self, value):
        """Return the board's status."""
        if not value in self.STATUS:
            raise ValueError('Invalid board status')
        if isinstance(value, str):
            value = self.STATUS[value]
        self._status = value

    @property
    def to_json(self):
        """Return object as json string property."""
        hands = {}
        for key, hand in self.hands.items():
            hands[key] = hand.to_json
        tricks = []
        for trick in self.tricks:
            tricks.append(trick.to_json)
        json_str = json.dumps({
            'auction': self.auction.to_json,
            'bid_history': self.bid_history,
            'contract': self.contract.to_json,
            'current_player': self.current_player,
            'current_trick': self.current_trick.to_json,
            'declarer': self.declarer,
            'declarer_index': self.declarer_index,
            'dealer': self.dealer,
            'dealer_index': self.dealer_index,
            'description': self.description,
            'east': self.east,
            'EW_tricks': self.EW_tricks,
            'hands': hands,
            'identifier': self.identifier,
            'north': self.north,
            'NS_tricks': self.NS_tricks,
            'play_status': self.play_status,
            'play_master': self.play_master,
            'south': self.south,
            'stage': self._stage,
            'reset': self.reset,
            'tricks': tricks,
            'vulnerable': self.vulnerable,
            'west': self.west,
        })
        return json_str

    def from_json(self, json_str):
        """Populate attributes from json string."""
        board_dict = dict(json.loads(json_str))
        self._auction = Auction(json.loads(board_dict['auction']))
        self.bid_history = board_dict['bid_history']
        contract = json.loads(board_dict['contract'])
        self._contract = Contract(name=contract['name'], declarer=contract['declarer'])
        self.current_player = board_dict['current_player']
        self.declarer = board_dict['declarer']
        self.declarer_index = int(board_dict['declarer_index'])
        self.dealer = board_dict['dealer']
        self.dealer_index = int(board_dict['dealer_index'])
        self.description = board_dict['description']
        self.east = board_dict['east']
        self.EW_tricks = int(board_dict['EW_tricks'])
        self.hands = {}
        hands = board_dict['hands']
        for key, raw_hand in hands.items():
            hand = Hand()
            hand.from_json(raw_hand)
            if key.isnumeric():
                key = int(key)
                self.players[key].hand = hand
            self.hands[key] = hand
        self.identifier = board_dict['identifier']
        self.NS_tricks = int(board_dict['NS_tricks'])
        self.play_status = int(board_dict['play_status'])
        self.play_master = board_dict['play_master']
        self.reset = board_dict['reset']
        self.south = board_dict['south']
        self._stage = board_dict['stage']
        self.tricks = []
        for raw_trick in board_dict['tricks']:
            trick = Trick()
            trick.from_json(raw_trick)
            self.tricks.append(trick)
        trick = Trick()
        if 'current_trick' in board_dict:
            self.current_trick = trick.from_json(board_dict['current_trick'])
        else:
            self.current_trick = trick
        self.vulnerable = board_dict['vulnerable']
        self.west = board_dict['west']

    @property
    def auction(self):
        """Return auction property."""
        return self._auction

    @auction.setter
    def auction(self, value):
        """Set auction property."""
        self._auction = value
        if value:
            self._contract = self.get_contract()

    @property
    def stage(self):
        """Assign stage property."""
        return self._stage

    @stage.setter
    def stage(self, value):
        """Set stage property."""
        self._stage = value

    def deal_from_pbn(self, pbn_string):
        """Create a deal from pbn_string."""
        pass

    def set_description(self, description):
        """Set the Board description."""
        self.description = description


    def get_auction(self, test=False):
        """Generate the auction."""
        if test:
            player_index = 0
        else:
            player_index = self.dealer_index
        auction_calls = []
        self.bid_history = []
        while not self.three_final_passes(auction_calls):
            player = self.players[player_index]
            bid = player.make_bid()
            auction_calls.append(bid)
            player_index += 1
            player_index %= 4
        auction = Auction()
        auction.calls = auction_calls
        return auction

    @staticmethod
    def three_final_passes(calls):
        """Return True if there have been three consecutive passes."""
        three_passes = False
        if len(calls) >= 4:
            if calls[-1].is_pass and calls[-2].is_pass and calls[-3].is_pass:
                three_passes = True
        return three_passes

    @staticmethod
    def _default_hands():
        hands = []
        dummy_hand = ['AS', 'KS', 'QS', 'JS', 'TS', '9S', '8S',
                      '7S', '6S', '5S', '4S', '3S', '2S']
        hands.append(Hand(dummy_hand))
        dummy_hand = [hand.replace('S', 'H') for hand in dummy_hand]
        hands.append(Hand(dummy_hand))
        dummy_hand = [hand.replace('H', 'D') for hand in dummy_hand]
        hands.append(Hand(dummy_hand))
        dummy_hand = [hand.replace('D', 'C') for hand in dummy_hand]
        hands.append(Hand(dummy_hand))
        return hands

    def parse_pbn_deal(self, deal, delimiter=":"):
        """Return a list of hands from a pbn deal string."""
        # example deal
        #   ['[Board "Board 1"]', '[Dealer "N"]',
        #    '[Deal "N:JT84.A987.8.T982 AKQ.KQ54.KQ2.A76 7652.JT3.T9.KQJ5 93.62.AJ76543.43"]']
        # hands = [None, None, None, None]
        # # Assign hands to board in correct position
        # self._dealer = deal[0]
        # hand_index = self._get_pbn_dealer_index(deal)
        # raw_hands = deal[2:].split(delimiter)
        # for card_list in raw_hands:
        #     hand = Hand(card_list)
        #     hands[hand_index] = hand
        #     hand_index = (hand_index + 1) % 4
        event = parse_pbn(deal)[0]
        board = event.boards[0]
        self.description = board.description
        self.dealer = board.dealer
        self.hands = {}
        for key, hand in board.hands.items():
            self.hands[key] = Hand(hand.cards)
        for index in range(4):
            self.players[index].hand = self.hands[index]
        return board.hands

    def _get_pbn_dealer_index(self, deal):
        """
            Return the first hand index to ensure that the first hand
            assigned to the board's hands list is that of the board dealer.
        """
        # first_hand is the position index of the first hand given in the deal
        first_hand = SEATS.index(deal[0])

        # dealer_index is the position index of the dealer
        dealer_index = SEATS.index(self.dealer)

        # rotate the hand index to ensure that the
        # first hand created is the dealer's
        hand_index = (first_hand - dealer_index) % 4
        return hand_index

    def create_pbn_list(self):
        """Return a board as a list of strings in pbn format."""
        deal_list = ['[Event "bfg generated deal"]',
                     '[Date "{}"]'.format(datetime.now().strftime('%Y.%m.%d')),
                     '[Board "{}"]'.format(self.description),
                     '[Dealer "{}"]'.format(self.dealer),
                     '[Deal "{}:{}"]'.format(self.dealer, self._get_deal_pbn(' ')),
                     '']
        return deal_list

    def _get_deal_pbn(self, delimiter=' '):
        """Return a board's hands as a string in pbn format."""
        hands_list = []
        for _, hand in self.hands.items():
            hand_list = []
            for _ in range(4):
                hand_list.append(['']*13)
            for card in hand.cards:
                suit = 3 - card.suit.rank
                rank = 13 - RANKS.index(card.rank)
                hand_list[suit][rank] = card.name[0]
            for index in range(4):
                hand_list[index] = ''.join(hand_list[index])
            hands_list.append('.'.join(hand_list))
        return delimiter.join(hands_list)

    @staticmethod
    def rotate_board_hands(board, increment=1):
        """Return the hands rotated through increment clockwise."""
        rotated_hands = {}
        hands = board.hands
        for index in range(4):
            rotated_index = (index + increment) % 4
            if index in hands:
                rotated_hands[rotated_index] = hands[index]
                board.players[rotated_index].hand = hands[index]
            if SEATS[index] in hands:
                rotated_hands[SEATS[rotated_index] ] = hands[SEATS[index]]
        board.hands = rotated_hands
        return board

    def get_contract(self):
        """Return a contract from the auction."""
        contract = Contract()
        if self._auction:
            if (self._three_final_passes(self._auction.calls) and
                    not self._passed_out(self._auction.calls)):
                dealer_index = SEATS.index(self.dealer)

                auction_calls = [call for call in self._auction.calls]
                auction_calls.reverse()
                for call in auction_calls:
                    if call.is_value_call:
                        break

                denomination = call.denomination
                for index, check_call in enumerate(self._auction.calls):
                    if check_call.denomination == denomination:
                        break
                declarer_index = (dealer_index + index) % 4
                declarer = SEATS[declarer_index]
                contract = Contract(call.name, declarer)
        return contract

    @staticmethod
    def _passed_out(calls):
        """Return True if the board has been passed out."""
        if len(calls) != 4:
            return False
        for call in calls:
            if not call.is_pass:
                return False
        return True

    @staticmethod
    def _three_final_passes(calls):
        """Return True if there have been three consecutive passes."""
        three_passes = False
        if len(calls) >= 4:
            if calls[-1].is_pass and calls[-2].is_pass and calls[-3].is_pass:
                three_passes = True
        return three_passes

    def get_attributes_from_board(self, board):
        """Set the attributes of this object from a board instance."""
        for key, item in board.__dict__.items():
            self.__dict__[key] = item
        for key, raw_hand in board.hands.items():
            hand = Hand(raw_hand.cards)
            board.hands[key] = hand
        for index in range(4):
            self.players[index].hand = board.hands[index]

        self.auction = Auction()
        for key, item in board.auction.__dict__.items():
            self.auction.__dict__[key] = item
