

class Found:
    def __init__(self, yt, caption, caption_time):
        self.yt = yt
        self.caption = caption
        self.caption_time = caption_time

    def __repr__(self):
        return f'<Found object -> video id:{self.yt.id},caption:{self.caption},time:{self.caption_time}'
