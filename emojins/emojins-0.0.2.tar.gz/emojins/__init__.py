from textblob import TextBlob

def use_emojins(text):
    textblob = TextBlob(text)
    sentiment = textblob.sentiment
    if sentiment.polarity < 0:
        emoji = "😭"
    elif sentiment.polarity < 0.5:
        emoji = "😐"
    elif sentiment.polarity > 0.5 and sentiment.polarity < 1:
        emoji = "😌"
    elif sentiment.polarity >= 1 and sentiment.polarity < 1.5:
        emoji = "😊"
    else:
        emoji = "😆✨"
    
    return print(text + emoji)
