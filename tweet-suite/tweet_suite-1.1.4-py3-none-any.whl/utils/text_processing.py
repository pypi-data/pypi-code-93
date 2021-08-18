"""Module containing functions used for text processing in others modules."""

import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# For VADER
analyzer = SentimentIntensityAnalyzer()


def process_text(tweet: str):
    """Removes the emojis, mentions and special characters from a tweet."""

    return " ".join(
        re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()
    )


def vader(tweet):
    return analyzer.polarity_scores(tweet)
