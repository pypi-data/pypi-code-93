import speech_recognition as sr 

def  AI_SpeechRecognition(pause_threshold_set, timeout_set, time_limit_set, language_set): ##AI_Speech(1, 4, 7, 'en-in')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("listening...")
        r.pause_threshold = pause_threshold_set
        # r.adjust_for_ambient_noise(source)
        # audio = r.listen(source)
        audio = r.listen(source,timeout=timeout_set,phrase_time_limit=time_limit_set)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language=language_set)
        print(f"user said: {query}")

    except Exception as e:
        # speak("Say that again please...")
        return "none"
    query = query.lower()
    return query

