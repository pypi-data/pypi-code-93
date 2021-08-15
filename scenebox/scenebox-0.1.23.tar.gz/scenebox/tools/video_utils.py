"""Miscellaneous (catch all) tools Copyright 2020 Caliber Data Labs."""

#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
from typing import NamedTuple


class VideoProperties(NamedTuple):
    width: int
    height: int
    fps: float
    duration: float
    num_frames: int


def get_video_attributes(video_uri: str) -> VideoProperties:
    import ffmpeg

    info = ffmpeg.probe(video_uri)
    return VideoProperties(
        width=int(info['streams'][0]['width']),
        height=int(info['streams'][0]['height']),
        duration=float(info['streams'][0]['duration']),
        num_frames=int(info['streams'][0]['nb_frames']),
        fps=eval(info['streams'][0]['avg_frame_rate']),
    )
