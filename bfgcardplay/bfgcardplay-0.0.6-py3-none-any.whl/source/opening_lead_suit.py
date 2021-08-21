""" Opening leads for Card Player class."""

from bridgeobjects import SUITS, Spades, Hearts, Diamonds, Clubs, SEATS, Contract, Denomination, Call

from .card_player_components import SelectedSuit, Card


def opening_lead_suit(board):
    """Return the opening lead from a list of cards given the contract."""
    return OpeningLeadSuit(board).suit


class OpeningLeadSuit():
    """Generate a suit for the opening lead."""
    def __init__(self, board, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        # board.contract = Contract(auction=board.auction)
        board.declarer = board.contract.declarer
        self.board = board
        self.contract = board.contract
        self.hand = board.hands[board.contract.leader]
        (leaders_bids, partners_bids, declarers_bids, dummys_bids, opponents_bids)  = self._allocate_bids()
        self.leaders_bids = leaders_bids
        self.partners_bids = partners_bids
        self.declarers_bids = declarers_bids
        self.dummys_bids = dummys_bids
        self.opponents_bids = opponents_bids
        self.denomination = self.contract.denomination
        self.opponents_suits = self._opponents_suits()
        self.unbid_suits = self._unbid_suits()

        # Generate the resulting suit
        self.suit = self._opening_lead_suit()

    def _allocate_bids(self):
        """Return partner's bids and opponent's bids."""
        board = self.board
        auction, dealer, leader = board.auction, board.dealer, board.contract.leader
        dealer_index = SEATS.index(dealer)
        leader_index = SEATS.index(leader)
        dummy_index = (leader_index + 1) % 4
        partner_index = (leader_index + 2) % 4
        declarer_index = (leader_index + 3) % 4
        leaders_bids = []
        partners_bids = []
        declarers_bids = []
        dummys_bids = []
        opponents_bids = []
        opponents_dealt = (SEATS.index(dealer) - SEATS.index(leader)) % 2
        for index, call in enumerate(auction.calls):
            miss_call = 99
            if self.contract.trump_suit:
                if call == Call('4NT') or call == Call('5NT'):
                    miss_call = index + 2
            if call.is_value_call and not index == miss_call:
                if (index + opponents_dealt) % 2:
                    opponents_bids.append(call)
                if not call.is_pass and (dummy_index - dealer_index - index) % 4 == 0:
                    dummys_bids.append(call)
                elif not call.is_pass and (declarer_index - dealer_index - index) % 4 == 0:
                    declarers_bids.append(call)
            if not call.is_pass and (partner_index - dealer_index - index) % 4 == 0:
                partners_bids.append(call)
            elif not call.is_pass and (leader_index - dealer_index - index) % 4 == 0:
                leaders_bids.append(call)
        return (leaders_bids, partners_bids, declarers_bids, dummys_bids, opponents_bids)

    def _opening_lead_suit(self):
        """Return the opening lead."""
        if self.denomination.is_nt:
            suit = self._select_suit_for_nt_contract()
        else:
            assert self.denomination, 'No trump suit defined for suit contract.'
            suit = self._select_suit_for_suit_contract()
        return suit

    def _select_suit_for_nt_contract(self):
        """Return the selected suit for a NT contract."""
        if self.contract.level >= 6:
            return self._select_suit_for_nt_slam_contract()
        if self.opponents_bids and self.opponents_bids[0].level >=3:
            return self._select_suit_for_preempt_nt_contract()

        blind = True
        for call in self.opponents_bids:
            if call.is_suit_call:
                blind = False
                break
        for call in self.partners_bids:
            if call.is_suit_call:
                blind = False
                break
        if blind:
            return self._select_suit_for_blind_nt_contract()
        return self._select_suit_for_informed_nt_contract()

    def _opponents_suits(self):
        """Return a list of suits in opponents_bids."""
        if (len(self.opponents_bids) > 1 and
                self.opponents_bids[0].is_nt and
                self.opponents_bids[1].denomination == Clubs()):
            return self._stayman_suits()
        else:
            opponents_suits = []
            for bid in self.opponents_bids:
                if bid.denomination not in opponents_suits:
                    opponents_suits.append(bid.denomination)
            return opponents_suits

    def _stayman_suits(self):
        """Return the suits implied by stayman bids."""
        opponents_suits = []
        if self.opponents_bids[2].denomination == Diamonds():
            return [Hearts(), Spades()]
        if self.opponents_bids[2].denomination == Hearts() and self.opponents_bids[3].is_nt:
            return [Hearts(), Spades()]
        if self.opponents_bids[2].denomination == Spades() and self.opponents_bids[3].is_nt:
            return [Hearts(), Spades()]
        if self.opponents_bids[2].denomination == Spades():
            return [Spades()]
        if self.opponents_bids[2].denomination == Hearts():
            return [Hearts()]


    def _unbid_suits(self):
        """Return a list of unbid majors given opponents_bids."""
        unbid_suits = [suit for suit in SUITS]
        for bid in self.opponents_bids:
            if bid.denomination in unbid_suits:
                unbid_suits.remove(bid.denomination)
        return unbid_suits

    def _select_suit_for_nt_slam_contract(self):
        """Return the selected suit for an NT slam contract."""
        sequences = self.hand.honour_sequences()
        for suit in SUITS:
            if sequences[suit]:
                suit = SelectedSuit(suit, '002')
                return suit
            if self.hand.suit_holding[suit] >= 3 and self.hand.honours[suit] == 0:
                suit = SelectedSuit(suit, '022')
                return suit
        return None

    def _select_suit_for_preempt_nt_contract(self):
        """Return the selected suit for an NT contract after preempt."""
        # Select suit with most High Card Points
        high_card_points = 0
        best_suit = None
        for suit in SUITS:
            suit_high_card_points = self.hand.suit_points(suit)
            if suit_high_card_points > high_card_points:
                high_card_points = suit_high_card_points
                best_suit = suit
        if best_suit:
            return SelectedSuit(best_suit, '021')
        return SelectedSuit(self.hand.longest_suit.name, '021')

    def _select_suit_for_informed_nt_contract(self):
        """Return the selected suit for an NT contract (not blind)."""
        if (self.hand.shape[0] >= 5 and self._has_entries() and
                self.hand.longest_suit not in self.opponents_suits):
            return SelectedSuit(self.hand.longest_suit.name, '021')

        partners_suit = self._suit_bid_by_partner()
        if partners_suit:
            return partners_suit

        # Look for 4+ card unbid major
        four_card_major = self._biddable_major(4)
        if four_card_major:
            return four_card_major

        # Biddable long suit
        if self.hand.shape[0] >= 5 and self.hand.longest_suit not in self.opponents_suits:
            return self.hand.longest_suit

        # Look for 4 card suit
        four_card_suit = self._biddable_suit(4)
        if four_card_suit:
            return four_card_suit

        # Best 3 card major
        three_card_major = self._biddable_major(3)
        if three_card_major:
            return three_card_major

        # Look for 3 card suit
        three_card_suit = self._biddable_suit(3)
        if three_card_suit:
            return three_card_suit

        return self.hand.longest_suit

    def _biddable_major(self, suit_length):
        """Return longest biddable major based on suit length."""
        unbid_majors = []
        if self.hand.spades >= suit_length and Spades() not in self.opponents_suits:
            unbid_majors.append(Spades())
        if self.hand.hearts >= suit_length and Hearts() not in self.opponents_suits:
            unbid_majors.append(Hearts())
        if len(unbid_majors) > 1:
            if self.hand.spades > self.hand.hearts:
                return SelectedSuit('S', '019')
            if self.hand.hearts > self.hand.spades:
                return SelectedSuit('H', '019')
            # Select better suit
            if self.hand.honours['S'] > self.hand.honours['H'] and self.hand.honours['S'] > 1:
                return SelectedSuit('S', '019')
            if self.hand.honours['H'] > self.hand.honours['S'] and self.hand.honours['H'] > 1:
                return SelectedSuit('H', '019')
        if unbid_majors:
            suit_name = unbid_majors[0].name
            if self.hand.honours[suit_name] != 1:
                return SelectedSuit(suit_name, '019')
        return None

    def _biddable_suit(self, suit_length):
        """Return longest biddable suit based on suit length."""
        unbid_suits = []
        if self.hand.spades == suit_length and Spades() not in self.opponents_suits:
            unbid_suits.append(Spades())
        if self.hand.hearts == suit_length and Hearts() not in self.opponents_suits:
            unbid_suits.append(Hearts())
        if self.hand.diamonds == suit_length and Diamonds() not in self.opponents_suits:
            unbid_suits.append(Diamonds())
        if self.hand.clubs == suit_length and Clubs() not in self.opponents_suits:
            unbid_suits.append(Clubs())
        if len(unbid_suits) > 1:
            # Select best suit
            if Spades() in unbid_suits and self.hand.honours['S'] > 1:
                if (self.hand.honours['S'] > self.hand.honours['H'] and
                        self.hand.honours['S'] > self.hand.honours['D'] and
                        self.hand.honours['S'] > self.hand.honours['C']):
                    return SelectedSuit('S', '019')
            if Hearts() in unbid_suits and self.hand.honours['H'] > 1:
                if (self.hand.honours['H'] > self.hand.honours['D'] and
                        self.hand.honours['H'] > self.hand.honours['C']):
                    return SelectedSuit('H', '019')
            if Diamonds() in unbid_suits and self.hand.honours['D'] > 1:
                if (self.hand.honours['D'] > self.hand.honours['C']):
                    return SelectedSuit('D', '019')
            if Clubs() in unbid_suits and self.hand.honours['C'] > 1:
                return SelectedSuit('C', '019')
        if unbid_suits:
            suit_name = unbid_suits[0].name
            return SelectedSuit(suit_name, '019')
        return None


    def _has_entries(self):
        """Return True if the hand has outside entries."""
        suit_points = 0
        for suit in SUITS:
            if suit != self.hand.longest_suit:
                suit_points += self.hand.suit_points(suit)
        if suit_points >= 7:
            return True
        return False

    def _select_suit_for_blind_nt_contract(self):
        """Return the selected suit for a blind NT contract."""

        if self.hand.shape[0] >= 5:
            return self._select_long_suit_for_blind_nt_contract()

        return self._select_four_card_suit_for_blind_nt_contract()

    def _select_long_suit_for_blind_nt_contract(self):
        """Return the selected long suit for a blind NT contract."""
        # honour sequences
        best_suit_with_sequence = self._best_suit_with_sequence()
        # best_suit_with_near_sequence = self._best_suit_with_near_sequence()
        # best_suit_with_interior_sequence = self._best_suit_with_interior_sequence()

        # the number of honours in the longest suit
        long_suit_honours = self.hand.honours[self.hand.longest_suit.name]

        # Select the best long suit with a 3 card sequence.
        if best_suit_with_sequence:
            suit = best_suit_with_sequence
            suit.selection_reason = '002'
            return suit

        # Select a long suit with multiple honours.
        if self.hand.shape[0] >= 5 and long_suit_honours >= 2:
            suit = SelectedSuit(self.hand.longest_suit.name, selection_reason='001')
            return suit

        # Select from best 5+ card suit
        if self.hand.shape[0] == self.hand.shape[1]:
            long_suits = self._equal_long_suits()
            suit = self._select_from_equal_long_suits(long_suits)
            return suit

        suit = SelectedSuit(self.hand.longest_suit.name, selection_reason='003')
        return suit

    def _select_four_card_suit_for_blind_nt_contract(self):
        """Return the selected 4 card suit for a blind NT contract."""
        # honour sequences
        best_suit_with_sequence = self._best_suit_with_sequence()
        best_suit_with_near_sequence = self._best_suit_with_near_sequence()
        best_suit_with_interior_sequence = self._best_suit_with_interior_sequence()

        # Select best 4 card suit with a sequence
        if best_suit_with_sequence:
            suit = best_suit_with_sequence
            suit.selection_reason = '010'
            return suit

        # Select best 4 card suit with a  near sequence
        if best_suit_with_near_sequence:
            suit = best_suit_with_near_sequence
            suit.selection_reason = '011'
            return suit

        # Select best 4 card suit with an interior sequence
        if best_suit_with_interior_sequence:
            suit = best_suit_with_interior_sequence
            suit.selection_reason = '012'
            return suit

        # Select best 4 card suit
        if self.hand.shape[0] == self.hand.shape[1]:
            suit = self._select_best_four_card_suit()
            suit.selection_reason = '006'
            return suit

        suit = SelectedSuit(self.hand.longest_suit.name, selection_reason='005')
        return suit

    def _select_best_four_card_suit(self):
        """Select the better of two 4 card suits."""
        four_card_suits = self._equal_long_suits()

        # Reject suits with AQxx or KJxx
        if self.contract.trump_suit:
            four_card_suits = self._remove_tenaces(four_card_suits)

        if len(four_card_suits) == 1:
            return (four_card_suits[0], '010')

        if not four_card_suits:
            four_card_suits = self._equal_long_suits()
        suit = self._select_from_equal_long_suits(four_card_suits)
        return suit

    def _select_from_equal_long_suits(self, long_suits):
        """Select the best suit from equal length by number of honours."""
        # Create a list of suits with maximum length for the hand.
        long_suits = self._equal_long_suits()

        # Find if one suit is headed by an Ace and the other(s) are not.
        non_ace_suits = self._non_ace_suits(long_suits)
        if len(non_ace_suits) == 1:
            suit = non_ace_suits[0]
            suit.selection_reason = '007'
            return suit

        elif len(non_ace_suits) > 1:
            long_suits = non_ace_suits

        # Find suits with touching honours
        touching_honours = self.hand.touching_honours()
        touching_honour_suits = []
        for suit in long_suits:
            if touching_honours[suit.name]:
                touching_honour_suits.append(suit)
        if len(touching_honour_suits) == 1:
            touching_honour_suits[0].selection_reason = '009'
            return touching_honour_suits[0]
        elif len(touching_honour_suits) >= 2:
            long_suits = touching_honour_suits

        # Find the maximum number of honours in the long suits.
        most_honours = self._most_honours(long_suits)

        # Create a list of long suits with that number of honours.
        suits_with_honours = self._suits_with_most_honours(long_suits, most_honours)

        # Select the suit with the best honours.
        if len(suits_with_honours) > 1:
            # Find the maximum honour points in long suits.
            suit = self._best_of_long_suits_with_honours(suits_with_honours)
        else:
            suit = suits_with_honours[0]
        suit.selection_reason = '004'
        return suit

    def _remove_tenaces(self, candidate_suits):
        """Remove suits with tenaces from a list of suits."""
        candidates = [suit for suit in candidate_suits]
        for suit in candidates:
            if ((Card(f'A{suit.name}') in self.hand.cards and
                    Card(f'Q{suit.name}') in self.hand.cards and
                    Card(f'K{suit.name}') not in self.hand.cards) or
                    (Card(f'K{suit.name}') in self.hand.cards and
                    Card(f'J{suit.name}') in self.hand.cards and
                    Card(f'Q{suit.name}') not in self.hand.cards)):
                candidate_suits.remove(suit)
        return candidate_suits

    def _most_honours(self, suit_list):
        """Return the maximum number of honours in a list of suits."""
        most_honours = -1
        for suit in suit_list:
            honours = self.hand.honours[suit.name]
            if honours > most_honours:
                most_honours = honours
        return most_honours

    def _suits_with_most_honours(self, suit_list, most_honours):
        """Return a list of suits with the given number of honours."""
        long_suits = []
        for suit in suit_list:
            honours = self.hand.honours[suit.name]
            if honours == most_honours:
                long_suits.append(suit)
        return long_suits

    def _best_of_long_suits_with_honours(self, suit_list):
        """Return the best of suits with honours."""
        max_honour_points = self._most_honour_points(suit_list)
        honour_suits = self._suits_with_honour_points(suit_list, max_honour_points)
        if len(honour_suits) == 1:
            suit = SelectedSuit(honour_suits[0].name)
        else:
            max_value = self._highest_suit_value(honour_suits)
            value_suits = self._get_suits_with_value(honour_suits, max_value)
            suit = value_suits[0]
        suit.selection_reason = '008'
        return suit

    def _equal_long_suits(self):
        """Return a list of suits of equal long length."""
        long_suits = []
        for suit_name, suit in SUITS.items():
            if self.hand.suit_holding[suit_name] == self.hand.shape[0]:
                long_suits.append(SelectedSuit(suit.name))
        return long_suits

    def _most_honour_points(self, suit_list):
        """Return the maximum number of honour points in a list of suits."""
        max_honour_points = -1
        for suit in suit_list:
            if self.hand.suit_points(suit) >= max_honour_points:
                max_honour_points = self.hand.suit_points(suit)
        return max_honour_points

    def _suits_with_honour_points(self, suit_list, max_honour_points):
        """Return a list of suits with the given honour points."""
        honour_suits = []
        for suit in suit_list:
            if self.hand.suit_points(suit) == max_honour_points:
                honour_suits.append(suit)
        return honour_suits

    def _best_suit_with_sequence(self):
        """Return the suit sequence with the highest honour."""
        sequences = self.hand.honour_sequences()

        # find length of longest sequences
        max_sequence_length = 0
        for suit_name, honours in sequences.items():
            if len(honours) > max_sequence_length:
                max_sequence_length = len(honours)
        if max_sequence_length == 0:
            return None

        # find suits with longest sequences in 4+ card suits
        long_sequences = []
        for suit_name, honours in sequences.items():
            if len(honours) == max_sequence_length:
                if self.hand.suit_holding[suit_name] >= 4:
                    suit = SelectedSuit(suit_name)
                    suit.sequence = sequences[suit_name]
                    long_sequences.append(suit)
        if len(long_sequences) == 0:
            return None
        if len(long_sequences) == 1:
            suit = long_sequences[0]
            return suit

        # find longest suit length with sequence
        longest_suit = 0
        for suit in long_sequences:
            if self.hand.suit_holding[suit.name] > longest_suit:
                longest_suit = self.hand.suit_holding[suit.name]

        # find longest suit with longest sequence
        long_suits = []
        for suit in long_sequences:
            if self.hand.suit_holding[suit.name] == longest_suit:
                long_suits.append(suit)
        if len(long_suits) == 1:
            suit = long_sequences[0]
            return suit

        # find the value of the highest card in a sequence
        top_value= 0
        for suit in long_suits:
            for card in sequences[suit.name]:
                if card.value > top_value:
                    top_value = card.value

        #  find highest ranking sequence
        ranking_suits = []
        for suit in long_suits:
            for card in sequences[suit.name]:
                if card.value == top_value:
                    ranking_suits.append(suit)
        if len(ranking_suits) == 1:
            suit = long_sequences[0]
            return suit

        # return major if equal rankng suits
        for suit_name in ranking_suits:
            if suit.is_major:
                return suit

        # more than one suit with equal credentials, so just return one of them
        suit = ranking_suits[0]
        return suit

    def _best_suit_with_near_sequence(self):
        """Return the near sequence with the highest honour."""
        candidates = []
        for suit_name in SUITS:
            if self.hand.suit_holding[suit_name] == 4:
                candidates.append(suit_name)
        if not candidates:
            return None
        for suit_name in candidates:
            suit = SelectedSuit(suit_name)
            if (Card(f'K{suit_name}') in self.hand.cards and
                    Card(f'Q{suit_name}') in self.hand.cards and
                    Card(f'T{suit_name}') in self.hand.cards):
                return suit
            elif (Card(f'Q{suit_name}') in self.hand.cards and
                    Card(f'J{suit_name}') in self.hand.cards and
                    Card(f'9{suit_name}') in self.hand.cards):
                return suit
            elif (Card(f'J{suit_name}') in self.hand.cards and
                    Card(f'T{suit_name}') in self.hand.cards and
                    Card(f'8{suit_name}') in self.hand.cards):
                return suit
            elif (Card(f'T{suit_name}') in self.hand.cards and
                    Card(f'9{suit_name}') in self.hand.cards and
                    Card(f'7{suit_name}') in self.hand.cards):
                return suit
        return None

    def _best_suit_with_interior_sequence(self):
        """Return the interior sequence with the highest honour."""
        candidates = []
        for suit in SUITS:
            if self.hand.suit_holding[suit] == 4:
                candidates.append(suit)
        if not candidates:
            return None
        for suit_name in candidates:
            suit = SelectedSuit(suit_name)
            if (Card(f'A{suit_name}') in self.hand.cards and
                    Card(f'Q{suit_name}') in self.hand.cards and
                    Card(f'J{suit_name}') in self.hand.cards):
                return suit
            elif (Card(f'K{suit_name}') in self.hand.cards and
                    Card(f'J{suit_name}') in self.hand.cards and
                    Card(f'T{suit_name}') in self.hand.cards):
                return suit
            elif (Card(f'Q{suit_name}') in self.hand.cards and
                    Card(f'T{suit_name}') in self.hand.cards and
                    Card(f'9{suit_name}') in self.hand.cards):
                return suit
            elif (Card(f'J{suit_name}') in self.hand.cards and
                    Card(f'9{suit_name}') in self.hand.cards and
                    Card(f'8{suit_name}') in self.hand.cards):
                return suit
            elif (Card(f'T{suit_name}') in self.hand.cards and
                    Card(f'8{suit_name}') in self.hand.cards and
                    Card(f'7{suit_name}') in self.hand.cards):
                return suit
        return None

    def _non_ace_suits(self, suit_list):
        """Return a list of suits with no ace if there is a long suit with an ace."""
        ace_suits = []
        non_ace_suits = []
        for suit in suit_list:
            card = Card(f'A{suit.name}')
            if card in self.hand.cards:
                ace_suits.append(suit)
            else:
                non_ace_suits.append(suit)
        if len(ace_suits) >= 1:
            return non_ace_suits
        else:
            return []

    def _highest_suit_value(self, suit_list):
        """Return the maximum suit value for a list of suits."""
        max_value = -1
        for suit in suit_list:
            cards = self.hand.cards_by_suit[suit.name]
            value = 0
            for card in cards:
                value += card.value
            if value > max_value:
                max_value = value
        return max_value

    def _get_suits_with_value(self, suit_list, max_value):
        """Return a list of suits with max_value."""
        value_suits = []
        for suit in suit_list:
            cards = self.hand.cards_by_suit[suit.name]
            value = 0
            for card in cards:
                value += card.value
            if value == max_value:
                value_suits.append(suit)
        return value_suits

    def _select_suit_for_suit_contract(self):
        """Return the selected suit for a suit contract."""
        # Order of selection based on Klinger's "Basic Bridge" p. 138
        denomination = self.denomination
        selected_suit = None

        selection_functions = [
            self._defend_against_slam,
            self._trump_after_double,
            self._dummy_has_long_suit,
            self._suit_with_AK,
            self._suit_with_sequence,
            self._suit_with_singleton,
            self._suit_bid_by_partner,
            self._partners_shortage,
            self._use_trumps,
            self._touching_honours,
            self._suit_if_not_deprecated,
            self._best_of_poor_suits,
        ]

        for selection_function in selection_functions:
            if self._no_selected_suit_or_no_cards(selected_suit):
                selected_suit = selection_function()
            else:
                break
        if self._no_selected_suit_or_no_cards(selected_suit):
            print('No suit found.', self.hand, self.denomination, self.opponents_bids)
            assert False, 'No suit found for suit contract.'
        return selected_suit

    def _defend_against_slam(self):
        """Return a suit against a slam bid."""
        if self.contract.level >= 6:
            if Call('D') in self.partners_bids:
                calls = [call for call in self.board.auction.calls]
                calls.reverse()
                double = False
                for call in calls:
                    if double:
                        if call.is_suit_call:
                            return SelectedSuit(call.denomination.name, '031')
                        else:
                            for dummys_call in self.dummys_bids:
                                if dummys_call.is_suit_call:
                                    return SelectedSuit(dummys_call.denomination.name, '032')
                    if call == Call('D'):
                        double = True
            if self.hand.hcp >= 7:
                for suit in SUITS:
                    if suit != self.contract.denomination.name:
                        if Card('K' + suit) in self.hand.cards:
                            return SelectedSuit(suit, '030')
            return None
        return None

    def _no_selected_suit_or_no_cards(self, selected_suit):
        """Return True if a suit has not been selected or the hand has no cards in that suit."""
        if not selected_suit:
            return True
        elif self.hand.cards_in_suit(selected_suit) == 0:
            return True
        return False

    def _suit_with_sequence(self):
        """Return the best suit with a sequence if any."""
        sequences = self.hand.honour_sequences()
        selected_suit = self._get_best_sequence_suit(sequences)
        if selected_suit:
            selected_suit.selection_reason = '002'
        return selected_suit

    def _trump_after_double(self):
        """Return the trump suit if partner has passed your takeout double."""
        partner_passed = True
        for call in self.partners_bids:
            if not call.is_pass:
                partner_passed = False
                break
        if Call('D') in self.leaders_bids and partner_passed:
            return SelectedSuit(self.contract.denomination.name, '028')

    def _dummy_has_long_suit(self):
        """Return the unbid suit if dummy has long suit."""
        if len(self.dummys_bids) < 2:
            return None
        denominations = {}
        for call in self.dummys_bids:
            if call.denomination in denominations:
                denominations[call.denomination] += 1
            else:
                denominations[call.denomination] = 0
        for denomination, value in denominations.items():
            if value:
                suit = self._equal_long_suits()[0]
                return SelectedSuit(suit.name, '029')
        return None


    def _suit_with_AK(self):
        """Return suit with an AK pairing."""
        candidate_suits = []
        for suit in SUITS:
            if suit != self.denomination.name:
                cards = self.hand.cards_by_suit[suit]
                if len(cards) >= 2:
                    if cards[0].rank == 'A' and cards[1].rank == 'K':
                        candidate_suits.append(suit)
        if len(candidate_suits) > 1:
            partners_suits = [call.denomination.name for call in self.partners_bids]
            for suit in candidate_suits:
                if suit in partners_suits:
                    return SelectedSuit(suit, '006')
        elif candidate_suits:
            return SelectedSuit(candidate_suits[0], '007')
        return None

    def _suit_with_singleton(self):
        """Return suit with a singleton."""
        trump_cards = self.hand.cards_by_suit[self.contract.name[1]]
        trump_hcp = 0
        for card in trump_cards:
            trump_hcp += card.high_card_points
        if trump_hcp >= 4 and len(trump_cards) >= 3:
            return None
        candidate_suits = []
        for suit_name, suit in SUITS.items():
            if suit != self.denomination:
                cards = self.hand.cards_by_suit[suit_name]
                if len(cards) == 1:
                    candidate_suits.append(suit)
        if candidate_suits:
            return SelectedSuit(candidate_suits[0].name, '008')
        return None

    def _suit_bid_by_partner(self):
        """Return suit bid by partner."""
        for call in self.partners_bids:
            if call.is_suit_call:
                return SelectedSuit(call.denomination.name, '020')
        return None

    def _suit_if_not_deprecated(self):
        """Return the best suit if not deprecated."""
        candidate_suits = self._non_deprecated_suits()
        if not candidate_suits:
            # print('suit_if_not_deprecated - A')
            return None

        if len(candidate_suits) == 1:
            # print(f'suit_if_not_deprecated {suit} - B')
            return SelectedSuit(candidate_suits[0], '014')

        for suit in candidate_suits:
            cards = self.hand.cards_by_suit[suit]
            honour = False
            for card in cards:
                if card.is_honour:
                    honour = True
                    break

            # print(f'suit_if_not_deprecated {suit} - C')
            # print('cs', suit, cards)

            # Select suit with two honours
            if self._suit_has_two_honours(suit, cards):
                # print(f'suit_if_not_deprecated {suit} - D')
                return SelectedSuit(suit, '015')

            # Select doubleton with no honour
            if len(cards) == 2 and not honour:
                # print(f'suit_if_not_deprecated {suit} - E')
                return SelectedSuit(suit, '016')

            # Select suit with no honours
            if not honour:
                # print(f'suit_if_not_deprecated {suit} - F')
                return SelectedSuit(suit, '017')
        # print(f'suit_if_not_deprecated {suit} - G')

        # Select the longest remaining suit
        max_length = max([self.hand.cards_by_suit[suit] for suit in candidate_suits])
        for suit in candidate_suits:
            cards = self.hand.cards_by_suit[suit]
            if len(cards) == max_length:
                return SelectedSuit(suit, '018')

    def _suit_has_two_honours(self, suit, cards):
        """Return True if the suit has at least two honours."""
        if Card(f'K{suit}') in cards and Card(f'Q{suit}') in cards:
            return True
        elif Card(f'K{suit}') in cards and Card(f'J{suit}') in cards:
            return True
        elif Card(f'K{suit}') in cards and Card(f'T{suit}') in cards:
            return True
        elif Card(f'Q{suit}') in cards and Card(f'J{suit}') in cards:
            return True
        elif Card(f'Q{suit}') in cards and Card(f'T{suit}') in cards:
            return True
        return False


    def _non_deprecated_suits(self):
        """Return a list of non-deprecated suits."""
        opposition_suits = [call.denomination.name
            for call in self.opponents_bids
            if call.is_suit_call
        ]
        candidate_suits = [suit for suit in SUITS]
        for suit in SUITS:
            remove = False
            cards = self.hand.cards_by_suit[suit]

            # Do not underlead an A
            if len(cards) >= 2 and cards[0].rank == 'A' and cards[1].rank != 'K':
                remove = True

            # Do not lead from a doubleton headed by an honour
            elif len(cards) == 2 and cards[0].high_card_points and cards[1].value <= Card('9S').value:
                remove = True

            # Do not lead a singleton trump
            elif suit == self.denomination.name and len(cards) == 1:
                remove = True

            # Ignore suits bid by opposition
            elif suit in opposition_suits:
                remove = True

            if remove:
                candidate_suits.remove(suit)
        return candidate_suits

    def _use_trumps(self):
        """Return the trump suit if it can be used."""
        cards = self.hand.cards_by_suit[self.denomination.name]
        if len(cards) >= 2 and not cards[0].high_card_points:
            return SelectedSuit(self.denomination.name, '028')
        return None

    def _get_best_sequence_suit(self, sequences):
        """Return the best suit sequence."""
        top_of_sequence = self._get_top_card_in_sequences(sequences)
        candidates = self._get_candidate_sequence_suits(sequences, top_of_sequence)
        if len(candidates) == 1:
            return SelectedSuit(candidates[0], '001')
        else:

            return self._get_best_suit_for_equal_rank_sequences(candidates)

    def _get_top_card_in_sequences(self, sequences):
        """Return the highest value card from a set of sequences."""
        top_of_sequence = 0
        for suit, sequence in sequences.items():
            if sequence:
                value = sequence[0].value
                if value > top_of_sequence:
                    top_of_sequence = value
        return top_of_sequence

    def _get_candidate_sequence_suits(self, sequences, top_of_sequence):
        """Return a list of suit sequences with equal top card."""
        length_of_sequence = 0
        candidates = []
        for suit, sequence in sequences.items():
            if suit != self.denomination.name:
                if sequence:
                    value = sequence[0].value
                    if value == top_of_sequence:
                        if len(sequence) >= length_of_sequence:
                            length_of_sequence = len(sequence)
                            candidates.append(suit)
        return candidates

    def _get_best_suit_for_equal_rank_sequences(self, candidate_suits):
        """Return the suit with the maximum length in sequences."""
        max_suit_length = 0
        suit_candidates = []
        for suit in candidate_suits:
            if self.hand.suit_holding[SelectedSuit(suit)] > max_suit_length:
                max_suit_length = self.hand.suit_holding[SelectedSuit(suit)]
        for suit in candidate_suits:
            if self.hand.suit_holding[SelectedSuit(suit)] == max_suit_length:
                suit_candidates.append(suit)
        if len(suit_candidates) == 1:
            return SelectedSuit(suit_candidates[0], '002')
        else:
            majors = []
            for suit in suit_candidates:
                if suit in 'SH':
                    majors.append(suit)
                if len(majors) == 1:
                    return SelectedSuit(majors[0], '003')
                elif len(majors) == 2:
                    suit_candidates = majors
        if len(suit_candidates) > 1:
            suit_candidates = self._get_suit_with_highest_value(suit_candidates)
        return suit_candidates

    def _get_suit_with_highest_value(self, suit_candidates):
        """Return the suit with  the highest aggregate card value."""
        ranking = 0
        chosen_suit = None
        for suit in suit_candidates:
            values = 0
            for card in self.hand.cards_by_suit[suit]:
                values += card.value
            if values > ranking:
                ranking = values
                chosen_suit = suit
        return SelectedSuit(chosen_suit, '004')

    def _touching_honours(self):
        """Return suit with touching honours."""
        touching_honours = self.hand.touching_honours()
        for suit in SUITS:
            if len(touching_honours[suit]) >= 2:
                return SelectedSuit(suit, '027')
        return None

    def _partners_shortage(self):
        """Return partners short suit."""
        last_suit = ''
        suit_fit = None
        for call in self.opponents_bids:
            if call.denomination == last_suit and call.denomination != self.contract.denomination:
                if call.is_suit_call:
                    suit_fit = call.denomination
                    break
            else:
                last_suit = call.denomination
        if suit_fit and len(self.hand.cards_by_suit[suit_fit.name]) >= 4:
            return SelectedSuit(suit_fit.name, '026')
        return None

    def _best_of_poor_suits(self):
        """Select best suit from poor choices."""
        suits = [Denomination(suit) for suit in SUITS if Denomination(suit) not in self.opponents_suits]
        deprecated_suits = []
        for suit in suits:
            cards = self.hand.cards_by_suit[suit.name]
            if cards[0].rank == 'A' and cards[1].rank != 'K':
                deprecated_suits.append(suit)
        for suit in deprecated_suits:
            suits.remove(suit)
        if len(suits) == 1:
            return SelectedSuit(suits[0].name, '016')
        # Use K high suit rather than Q etc.
        for suit in suits:
            cards = self.hand.cards_by_suit[suit.name]
            if Card('K'+ suit.name) in cards:
                return SelectedSuit(suits[0].name, '023')
            if Card('Q'+ suit.name) in cards:
                return SelectedSuit(suits[0].name, '024')
            if Card('J'+ suit.name) in cards:
                return SelectedSuit(suits[0].name, '025')



        cards = self.hand.cards_by_suit[self.hand.longest_suit.name]
        if cards[0].rank != 'A':
            selected_suit = SelectedSuit(self.hand.longest_suit.name, '005')
        else:
            selected_suit = SelectedSuit(self.hand.second_suit.name, '888')
        return selected_suit


    def xxx(self):
        """Return True if zzz."""
        result = False
        return result

    def xxx(self):
        """Return True if zzz."""
        result = False
        return result
