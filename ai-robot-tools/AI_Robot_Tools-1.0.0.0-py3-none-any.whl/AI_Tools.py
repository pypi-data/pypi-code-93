from googletrans import Translator
import datetime
import time
import pyttsx3

def Speak(value,speed,Text): #####Speak(0,150,'Hai I am Rishabh Kumar')
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    # print(voices[0].id)
    engine.setProperty('voices', voices[value].id)
    engine.setProperty('rate', speed)
    engine.say(Text)
    print(Text)
    engine.runAndWait()

def AI_Translate(Text,language):## AI_Translate('Hai I am Rishabh','hi')
    translate = Translator()
    result = translate.translate(Text,dest=language)
    Text_res = result.text
    return Text_res

def Wish_WithTime(morning,afternoon,evening,othertext): ## Wish_WithTime('good morning','good afternoon','good evening','Hai Help You')
    hour = int(datetime.datetime.now().hour)
    tt = time.strftime("%I:%M %p")

    if hour >= 0 and hour <= 12:
        print(f"{morning} {tt}")
    elif hour >= 12 and hour <= 18:
        print(f"{afternoon} {tt}")
    else:
        print(f"{evening} {tt}")
    print(othertext) 

def Wish(morning,afternoon,evening,othertext):## Wish('good morning','good afternoon','good evening','Hai Help You')
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour <= 12:
        print(morning)
    elif hour >= 12 and hour <= 18:
        print(afternoon)
    else:
        print(evening)
    print(othertext)    

def AI_Speak_Wish(morning,afternoon,evening,othertext):## AI_Speak_Wish('good morning','good afternoon','good evening','Hai Help You')
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour <= 12:
        aa=morning
        Speak(0,150,aa)
    elif hour >= 12 and hour <= 18:
        aa=afternoon
        Speak(0,150,aa)
    else:
        aa=evening
        Speak(0,150,aa)
    aa=othertext
    Speak(0,150,aa)    

def AI_Speak_Wish_WithTime(morning,afternoon,evening,othertext):## AI_Speak_Wish_WithTime('good morning','good afternoon','good evening','Hai Help You')
    hour = int(datetime.datetime.now().hour)

    tt = time.strftime("%I:%M %p")

    if hour >= 0 and hour <= 12:
        aa=(f"{morning} {tt}")
        Speak(0,150,aa)
    elif hour >= 12 and hour <= 18:
        aa=(f"{afternoon} {tt}")
        Speak(0,150,aa)
    else:
        aa=(f"{evening} {tt}")
        Speak(0,150,aa)
    aa=(othertext)
    Speak(0,150,aa)   
