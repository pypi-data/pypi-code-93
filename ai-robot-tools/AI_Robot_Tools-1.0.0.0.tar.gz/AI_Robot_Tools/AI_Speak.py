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

