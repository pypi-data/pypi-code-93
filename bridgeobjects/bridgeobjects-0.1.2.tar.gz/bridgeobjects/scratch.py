
import os


from source.file_operations import load_rbn, save_pbn, load_pbn
from source.hand import Hand
from source.card import Card
from source.trick import Trick



hand_list_6332 = ['JS', '8S', '5S', '4S', '3S', '2S',
                  'JH', '8H', '6H',
                  'AD', 'JD',
                  'KC', 'JC']


trick = Trick([Card('AH'), Card('2H'), Card('3H'), Card('4H')])
print(repr(trick))
trick = Trick(['KH', '2H', '3H', '4H'])
print(repr(trick))
trick = Trick([Card('AH'), Card('2H'), Card('3H'), Card('4H')])
print(str(trick))


# test cards ---------------------------------------
# hand.suit_order = 'HSDC'
# cards = hand.sorted_cards()
# print(cards)
# assert cards[0] == Card('KH')
# assert cards[3] == Card('AS')
# assert cards[-5] == Card('TD')
# assert cards[-1] == Card('6C')

# test hands ---------------------------------------
# hand_pbn_two = 'A8654.KQ5.T.QJT6'
# hand = Hand(hand_pbn_two)
# print(str(Hand(".63.AKQJ87.A9732")))
# assert str(Hand(hand_list_6332)) == 'Hand(JS, 8S, 5S, 4S, 3S, 2S, JH, 8H, 6H, AD, JD, KC, JC)'

# test file load ---------------------------------------
# DATA_PATH = '/home/jeff/.virtualenvs/cardplay/lib/python3.9/site-packages/bridgeobjects/test_data/'
# load_path = ''.join([DATA_PATH, 'pbn_input_file_1.pbn'])
# events_loaded = load_pbn(load_path)

# # Create a pbn file from a rbn input to test saves
# input_path = ''.join([DATA_PATH, 'rbn_input_file_1.rbn'])
# save_path = ''.join([DATA_PATH, 'pbn_output_file_1.pbn'])
# test_events = load_rbn(input_path)
# save_pbn(test_events, save_path)
# events_saved = load_pbn(save_path)