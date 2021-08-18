from textblob import TextBlob

def use_emojins(text):
    sub_text = text.lower()
    textblob = TextBlob(text)
    sentiment = textblob.sentiment

    if "?" in sub_text:
        emoji = " 😐❔"
        return print(text + emoji)

    party_list = ["birthday", "celebration", "party"]
    for word in party_list:
        if word in sub_text:
            emoji = " 🥳🎁🎊🎉🎈"
            return print(text + emoji)

    angry_list = ["angry", "irate", "disappoint", "frustrate"]
    for word in angry_list:
        if word in sub_text:
            emoji = " 😡"
            return print(text + emoji)

    if sentiment.polarity < -0.4:
        emoji = " 😭"
    elif sentiment.polarity <= 0:
        emoji = " 😢"
    elif sentiment.polarity < 0.5:
        emoji = " 😌"
    elif sentiment.polarity > 0.5 and sentiment.polarity < 1:
        emoji = " 🙂"
    elif sentiment.polarity >= 1 and sentiment.polarity < 1.5:
        emoji = " 😊"
    else:
        emoji = " 😆✨"
    
    return print(text + emoji)

use_emojins("impressive work")