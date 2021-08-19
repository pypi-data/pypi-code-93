"""prayer_tool"""
import sys
import os
import getopt
from datetime import time, date, datetime
from json import JSONDecodeError
import requests
from gtts import gTTS
from playsound import playsound
from googletrans import Translator

##get translator instance
translator = Translator()

##Declaring needed variables
salat_list = ["Fajr","Dhuhr","Asr","Maghreb","Isha"]
SCHOOL = 3
CURRENT_TIME = datetime.now().timestamp()
URL = "https://api.pray.zone/v2/times/today.json"
LOCATION = "Brussels"
DEST = "fr"
HELP_STRING = '\nArguments:\n -c <city> (default -> Brussels) \n -l <language> (default -> fr)\n'
ERROR_LINE = "An error occured, check for typos in the command line arguments or try again later"

##Getting all the command line arguments
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv,"hc:l:",["city=","lang="])
except getopt.GetoptError:
    print (HELP_STRING)
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print (HELP_STRING)
        sys.exit()
    elif opt in ("-c", "--city"):
        LOCATION = arg
    elif opt in ("-l", "--lang"):
        DEST = arg

def request_builder():
    """Creates the request with correct url and parameters"""
    params = {'city': LOCATION, 'school': SCHOOL}
    request = requests.get(url = URL, params=params)
    return request

def get_json():
    """makes the get request and returns raw json"""
    request = request_builder()
    data = request.json()
    return data

def format_time(temp_salat):
    """Format string hours to time object"""
    (hour, second) = temp_salat.split(':')
    return time(int(hour), int(second))

def get_timestamps(input_time):
    """Returns timestamps from given time parameter"""
    tod = date.today()
    today = datetime(tod.year, tod.month, tod.day,
    input_time.hour, input_time.minute, input_time.second)
    return datetime.timestamp(today)

def parse_json_to_timestamp_array():
    """Uses the raw JSON to create an array of timestamps"""
    times = get_json()["results"]["datetime"][0]["times"]
    salat_array = [times["Fajr"], times["Dhuhr"], times["Asr"], times["Maghrib"], times["Isha"]]
    time_array = []
    for sal in salat_array:
        time_array.append(get_timestamps(format_time(sal)))
    return time_array

def check_time():
    """Will compare current time with the salat to show the next one"""
    times = parse_json_to_timestamp_array()
    i = 0
    while i < 5:
        if CURRENT_TIME < times[i]:
            return datetime.fromtimestamp(times[i]), int(i)
        i += 1
    return 0, 0

def get_translation(ins, source):
    """Translates the output"""
    translated = translator.translate(ins,src=source ,dest=DEST)
    return translated

def play(text):
    """Plays the sound"""
    dire = "./out.mp3"
    output = get_translation(text, "fr")
	#Use the translated text to generate an mp3 file with it
    gTTS(output.text, lang=DEST).save(dire)
	#Plays the mp3 file
    playsound(dire)
    return dire

def speak():
    """Will generate a string and play it in the STT class"""
    next_salat, number = check_time()
    text = ""
    if next_salat != 0:
        difference = next_salat - datetime.fromtimestamp(CURRENT_TIME)
        sec = difference.total_seconds()
        result = ""
        minutes = int(sec/60)
        rest_minutes = int(sec/60 % 60)
        hours = int(minutes/60)
        if minutes >= 60:
            result = str(hours)+ " heures et "+  str(rest_minutes) +" minutes"
        else:
            result = str(minutes) + " minutes"
        text = f"La prière de {salat_list[number]} est dans {result}"
    else:
        text = "Toutes les prières sont déjà passées"
    return play(text)

def play_error(message):
    """Function to play the error messages"""
    path = "./error.mp3"
    gTTS(message, lang="en").save(path)
    playsound(path)
    os.remove(path)

def main():
    """Main function"""
    try:
        os.remove(speak())
    except JSONDecodeError:
        play_error("The city you have given is incorrect")
    except ValueError:
        play_error("The language you have given is incorrect")
