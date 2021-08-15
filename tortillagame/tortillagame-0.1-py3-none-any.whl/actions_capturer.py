class ActionsCapturer:
    def __init__(self):
        self._key_a = False
        self._key_left = False
        self._key_right = False
        self._key_up = False
        self._key_down = False
        self._key_escape = False
        self._key_v = False
        self._key_space = False

    def to_default(self):
        self._key_a = False
        self._key_left = False
        self._key_right = False
        self._key_up = False
        self._key_down = False
        self._key_escape = False
        self._key_v = False
        self._key_space = False

    @property
    def key_a(self): return self._key_a

    @property
    def key_left(self): return self._key_left

    @property
    def key_right(self): return self._key_right

    @property
    def key_up(self): return self._key_up

    @property
    def key_down(self): return self._key_down

    @property
    def key_escape(self): return self._key_escape

    @property
    def key_v(self): return self._key_v

    @property
    def key_space(self): return self._key_space

    @key_a.setter
    def key_a(self, value: bool): self._key_a = value

    @key_left.setter
    def key_left(self, value: bool): self._key_left = value

    @key_right.setter
    def key_right(self, value: bool): self._key_right = value

    @key_up.setter
    def key_up(self, value: bool): self._key_up = value

    @key_down.setter
    def key_down(self, value: bool): self._key_down = value

    @key_escape.setter
    def key_escape(self, value: bool): self._key_escape = value

    @key_v.setter
    def key_v(self, value: bool): self._key_v = value

    @key_space.setter
    def key_space(self, value: bool): self._key_space = value
