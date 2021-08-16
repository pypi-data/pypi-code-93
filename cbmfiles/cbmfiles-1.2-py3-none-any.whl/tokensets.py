
class TokenTrie:
    def __init__(self):
        self.root = dict()

    def add_token(self, text, token):
        """Associate a value with a string token."""
        current = self.root
        for c in text:
            current = current.setdefault(c.upper(), {})
        current['_t_'] = token

    def next_token(self, text):
        """Return either text and value of the next token or a string which matches no token."""
        if text[0].upper() not in self.root:
            # initial letter not in trie, no match
            return text[0], None

        current = self.root
        match_stack = []
        for i in range(0, len(text)):
            if text[i].upper() not in current:
                if '_t_' in current:
                    # prefix in trie
                    return text[:i], current['_t_']
                if match_stack:
                    # there is a shorter match
                    return match_stack.pop()
                # no match
                return text[0], None
            if '_t_' in current:
                match_stack.append((text[:i], current['_t_']))
            current = current[text[i].upper()]
        return text, current.get('_t_')


class TokenSet:
    def __init__(self):
        self.token_to_string = dict()
        self.string_to_token = TokenTrie()
        self.raw = False
        self.skip_tokenize_after = ()
        self.secondary_token = None

    def add_tokens(self, tokens):
        # populate token trie
        for s, t in tokens:
            self.string_to_token.add_token(s, t)
        if self.raw:
            new_tokens = {t: s for s, t in tokens}
        else:
            new_tokens = {t: s.encode() for s, t in tokens}
        self.token_to_string.update(new_tokens)

    def set_secondary_tokens(self, lead_token, tokens):
        self.secondary_token = lead_token
        for s, t in tokens:
            self.string_to_token.add_token(s, bytes([lead_token, t]))
        self.secondary_token_to_string = {t: s.encode() for s, t in tokens}

    def tokenize(self, line, encoding):
        ret = bytearray()
        while line:
            match_text, token = self.string_to_token.next_token(line)
            line = line[len(match_text):]
            if token is None:
                # no token, just encode text
                ret += match_text.encode(encoding)
            else:
                if isinstance(token, int):
                    ret.append(token)
                    if token in self.skip_tokenize_after:
                        # remainder of line is not to be tokenized
                        return ret+line.encode(encoding)
                else:
                    ret += token

        return ret

    def expand(self, line_encoded, encoding):
        ret = ''
        previous = None
        for b in line_encoded:
            if b in self.token_to_string:
                if self.raw or not self.token_to_string[b].isascii():
                    ret += self.token_to_string[b]
                else:
                    ret += self.token_to_string[b].decode(encoding)
            elif self.secondary_token is not None and previous == self.secondary_token and b in self.secondary_token_to_string:
                ret += self.secondary_token_to_string[b].decode(encoding)
            elif b != self.secondary_token:
                ret += bytes([b]).decode(encoding)
            previous = b
        return ret


_token_set_register = {}


def lookup(set_name):
    """Return the token set for a given name."""
    if set_name in _token_set_register:
        return _token_set_register[set_name]
    raise LookupError("unknown token set: "+set_name)


def token_set_names():
    return _token_set_register.keys()
