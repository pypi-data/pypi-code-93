from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(description="An auto downloader and uploader for TikTok videos.")
    parser.add_argument("user")
    parser.add_argument(
        "--no-delete", action="store_false", help="don't delete files once uploaded to the Internet Archive"
    )
    parser.add_argument(
        "--hashtag", action="store_true", help="download this hashtag"
    )
    parser.add_argument(
        "--limit", help="set limit on amount of TikToks to download"
    )
    parser.add_argument(
        "--use-download-archive",
        action="store_true",
        help=(
            "record the video url to the download archive. "
            "This will download only videos not listed in the archive file. "
            "Record the IDs of all downloaded videos in it."
        ),
    )
    parser.add_argument(
        "--id", action="store_true", help="download this video ID"
    )
    parser.add_argument(
        "--liked", action="store_true", help="download this user's liked posts"
    )
    parser.add_argument(
        "--folder", help="set download destination (default: ~/.tikup)"
    )
    parser.add_argument(
        "--no-upload", action="store_false", help="turn off uploading to the Internet Archive"
    )
    args = parser.parse_args()
    return args
