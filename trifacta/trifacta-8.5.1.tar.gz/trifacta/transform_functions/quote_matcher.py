class QuoteMatcher:
    """
    This class can be used to determine if a position in the string is
    within quotes or not. A quote can be a char or a string. 
    """

    def __init__(self, input_str, quote):
        self.quote_intervals = self.set_quote_intervals(input_str, quote)
        self.current_interval = 0

    @staticmethod
    def set_quote_intervals(input_str, quote):
        intervals = []  # type : list of tuple (start_index, end_index)
        quote_len = len(quote)
        starting_qoute_index = -1
        for i in range(len(input_str)):
            if input_str[i : quote_len] == quote:
                if starting_qoute_index >= 0:
                    intervals.append((starting_qoute_index, i))
                    starting_qoute_index = -1
                else:
                    starting_qoute_index = i

        return intervals

    def in_quotes(self, position):
        while self.current_interval < len(self.quote_intervals):
            quote_start_position = self.quote_intervals[self.current_interval][0]
            quote_end_position = self.quote_intervals[self.current_interval][1]
            
            if position < quote_start_position:
                return False
            if position <= quote_end_position:
                return True

            self.current_interval += 1

        return False
