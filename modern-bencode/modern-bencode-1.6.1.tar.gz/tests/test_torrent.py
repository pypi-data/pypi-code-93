"""Tests for torrent.py"""
import pytest

import bencode


def test_decode_encode_torrent(datadir):
    """Try to decode a torrent file"""
    torrent_data = datadir["big-buck-bunny.torrent"].read("rb")
    decoded_torrent = bencode.decode_torrent(torrent_data)
    encoded_torrent = bencode.encode_torrent(decoded_torrent)

    assert torrent_data == encoded_torrent

    assert decoded_torrent["info"]["pieces"].startswith("2020a7789d")
    decoded_torrent["info"]["pieces"] = []

    assert decoded_torrent == {
        "announce": "udp://tracker.leechers-paradise.org:6969",
        "announce-list": [
            ["udp://tracker.leechers-paradise.org:6969"],
            ["udp://tracker.coppersurfer.tk:6969"],
            ["udp://tracker.opentrackr.org:1337"],
            ["udp://explodie.org:6969"],
            ["udp://tracker.empire-js.us:1337"],
            ["wss://tracker.btorrent.xyz"],
            ["wss://tracker.openwebtorrent.com"],
            ["wss://tracker.fastcast.nz"],
        ],
        "comment": "WebTorrent <https://webtorrent.io>",
        "created by": "WebTorrent <https://webtorrent.io>",
        "creation date": 1490916601,
        "encoding": "UTF-8",
        "info": {
            "files": [
                {"length": 140, "path": ["Big Buck Bunny.en.srt"]},
                {"length": 276134947, "path": ["Big Buck Bunny.mp4"]},
                {"length": 310380, "path": ["poster.jpg"]},
            ],
            "name": "Big Buck Bunny",
            "piece length": 262144,
            "pieces": [],
        },
        "url-list": ["https://webtorrent.io/torrents/"],
    }


def test_decode_encode_torrent_utf8_suffix():
    """Dictionary keys, which have ".utf-8" suffix, should be decoded and
    encoded using this encoding, even if another encoding is specified in
    the function call
    """
    special_string = "日本語"
    special_string_as_bytes = special_string.encode("utf8")

    data = {b"path.utf-8": special_string_as_bytes}
    torrent_b = bencode.encode(data)
    torrent_p = {"path.utf-8": "日本語"}

    assert bencode.decode_torrent(torrent_b, "ascii") == torrent_p
    assert bencode.encode_torrent(torrent_p, "ascii") == torrent_b


def test_decode_torrent_unsupported_data_type():
    """Try to decode unsupported object (a text string)"""
    with pytest.raises(ValueError) as excinfo:
        bencode.decode_torrent("abcd")

    assert str(excinfo.value) == (
        "Cannot decode data, expected bytes, got <class 'str'> instead."
    )


def test_encode_torrent_unsupported_data_type():
    """Try to decode unsupported object (a text string)"""
    with pytest.raises(ValueError) as excinfo:
        bencode.encode_torrent("abcd")

    assert str(excinfo.value) == (
        "Cannot encode data, expected dict, got <class 'str'> instead."
    )
