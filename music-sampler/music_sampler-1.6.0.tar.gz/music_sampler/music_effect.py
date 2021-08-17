class GainEffect:
    effect_types = [
        'noop',
        'fade'
    ]

    def __init__(self, effect, audio_segment, initial_loop, start, end,
            **kwargs):
        if effect in self.effect_types:
            self.effect = effect
        else:
            self.effect = 'noop'

        self.start = start
        self.end = end
        self.audio_segment = audio_segment
        self.initial_loop = initial_loop
        getattr(self, self.effect + "_init")(**kwargs)

    def get_last_gain(self):
        return getattr(self, self.effect + "_get_last_gain")()

    def get_next_gain(self, current_frame, current_loop, frame_count):
        # This returns two values:
        # - The first one is the gain to apply on that frame
        # - The last one is True or False depending on whether it is the last
        #   call to the function and the last gain should be saved permanently
        return getattr(self, self.effect + "_get_next_gain")(
                current_frame,
                current_loop,
                frame_count)

    # Noop
    def noop_init(self, **kwargs):
        pass

    def noop_get_last_gain(self, **kwargs):
        return 0

    def noop_get_next_gain(self, **kwargs):
        return [0, True]

    # Fading
    def fade_init(self, gain=0, **kwargs):
        self.audio_segment_frame_count = self.audio_segment.frame_count()
        self.first_frame = int(
                self.audio_segment_frame_count * self.initial_loop +\
                self.audio_segment.frame_rate * self.start)
        self.last_frame = int(
                self.audio_segment_frame_count * self.initial_loop +\
                self.audio_segment.frame_rate * self.end)
        self.gain= gain

    def fade_get_last_gain(self):
        return self.gain

    def fade_get_next_gain(self, current_frame, current_loop, frame_count):
        current_frame = current_frame \
                + (current_loop - self.initial_loop) \
                    * self.audio_segment_frame_count

        if current_frame >= self.last_frame:
            return [self.gain, True]
        elif current_frame < self.first_frame:
            return [0, False]
        else:
            return [
                    (current_frame - self.first_frame) / \
                            (self.last_frame - self.first_frame) * self.gain,
                    False
                    ]


