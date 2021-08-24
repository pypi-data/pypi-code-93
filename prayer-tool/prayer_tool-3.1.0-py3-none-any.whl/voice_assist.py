"""prayer_tool"""
import sys
import getopt
from datetime import datetime
from json import JSONDecodeError
import tempfile
from gtts import gTTS
from playsound import playsound
from googletrans import Translator
from prayer_tool import prayer_times

##get translator instance
translator = Translator()
temp_dir = tempfile.TemporaryDirectory()

##Declaring needed variables
SCHOOL = 3
CURRENT_TIME = datetime.now().time()
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

##get prayer times instance
instance = prayer_times.PrayerTimes(city=LOCATION, school=SCHOOL)

def get_translation(ins, source):
    """Translates the output"""
    translated = translator.translate(ins,src=source ,dest=DEST)
    return translated

def play(text):
    """Plays the sound"""
    dire = temp_dir.name+"/out.mp3"
    output = get_translation(text, "fr")
	#Use the translated text to generate an mp3 file with it
    gTTS(output.text, lang=DEST).save(dire)
	#Plays the mp3 file
    playsound(dire)

def compare_time(time1, time2):
    """Returns the difference in minutes between two time objects"""
    minutes1 = int(time1.hour*60) + int(time1.minute)
    minutes2 = int(time2.hour*60) + int(time2.minute)
    return minutes2 - minutes1

def speak():
    """Will generate a string and play it in the STT class"""
    today_salat = instance.today()
    next_salat = today_salat.next_prayer()
    text = ""
    if next_salat is not None:
        difference = compare_time(CURRENT_TIME, next_salat.time)
        result = ""
        minutes = difference
        rest_minutes = int(minutes % 60)
        hours = int(minutes/60)
        if minutes >= 60:
            result = str(hours)+ " heures et "+  str(rest_minutes) +" minutes"
        else:
            result = str(minutes) + " minutes"
        text = f"La prière de {next_salat.name} est dans {result}"
    else:
        text = "Toutes les prières sont déjà passées"
    play(text)

def play_error(message):
    """Function to play the error messages"""
    path = temp_dir.name+"/error.mp3"
    gTTS(message, lang="en").save(path)
    playsound(path)

def main():
    """Main function"""
    try:
        speak()
    except JSONDecodeError:
        play_error("The city you have given is incorrect")
    except ValueError:
        play_error("The language you have given is incorrect")

if __name__ == "__main__":
    main()
    temp_dir.cleanup()
