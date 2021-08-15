class ArgParser():
    _OTHER_ARGS_NAME = "other_args"

    def __init__(self, shortopts:str, longopts:[str]):
        import re
        if self._OTHER_ARGS_NAME in longopts:
            raise ValueError \
                (f'Collision between self.OTHER_ARGS_NAME and self.longopts. This should never happend. collision word: "{self._OTHER_ARGS_NAME}"')
        self._shortopts = shortopts
        self._longopts = longopts
        for char in self._shortopts:
            if not re.search(r'[a-zA-Z:]', char):
                raise ValueError(f'Only expecting letters in shortopts. Got "{char}".')
            if char != ':':
                self.__setattr__(char, None)
        for longopt in longopts:
            self.__setattr__(longopt, None)
        self.__setattr__(self._OTHER_ARGS_NAME, None)
        self.getopt()


    def getopt(self, parse_string=None):
        import getopt, sys
        if parse_string is None:
            parse_string = sys.argv[1:]
        opts, args = getopt.getopt(parse_string, self._shortopts, self._longopts)
        optdict = dict(opts)
        for key in optdict.keys():
            if key[0:2] == "--":
                self.__setattr__(key[2:], optdict[key])
            else:
                self.__setattr__(key[1:], optdict[key])
        self.__setattr__(self._OTHER_ARGS_NAME, args)