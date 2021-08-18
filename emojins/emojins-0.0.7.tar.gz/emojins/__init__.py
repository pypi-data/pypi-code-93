from textblob import TextBlob

def use_emojins(text):
    text = text.lower()
    textblob = TextBlob(text)
    sentiment = textblob.sentiment

    if "?" in text:
        emoji = " 😐❔"
        return print(text + emoji)

    party_list = ["happy birthday", "birthday", "celebration", "party"]
    for word in party_list:
        if word in text:
            emoji = " 🥳🎁🎊🎉🎈"
            return print(text + emoji)

    angry_list = ["angry", "irate", "disappoint", "frustrate"]
    for word in angry_list:
        if word in text:
            emoji = " 😡"
            return print(text + emoji)
            
    happy_list = ["happy", "great", "awesome", "great", "good", "best"]
    for word in happy_list:
        if word in text:
            emoji = " 😊"
            return print(text + emoji)

    sad_list = ["sad", "depressing", "cry", "crying", "heartbreaking"]
    for word in sad_list:
        if word in text:
            emoji = " 😢"
            return print(text + emoji)

    if sentiment.polarity < -0.5:
        emoji = " 😭"
    elif sentiment.polarity >= -0.5 and sentiment.polarity < -0.9:
        emoji = " 😢"
    elif sentiment.polarity < 0.5:
        emoji = " 😐"
    elif sentiment.polarity > 0.5 and sentiment.polarity < 1:
        emoji = " 😌"
    elif sentiment.polarity >= 1 and sentiment.polarity < 1.5:
        emoji = " 😊"
    else:
        emoji = " 😆"
    
    return print(text + emoji)