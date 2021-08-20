import requests
from gtts import gTTS
from pygame import mixer
# import playsound

language = "en"
url = "https://random-word-api.herokuapp.com/"
choices = ["word", "all"]
location = "sound.mp3"

# Score out of 10
def main():
    score = 0
    def game():
        response = requests.get(url + choices[0])

        readable_data = response.json()[0]


        my_obj = gTTS(text=readable_data, lang=language, slow=False)
        my_obj.save(location)

        def guess_word():
            nonlocal score
            mixer.init()
            mixer.music.load(location)

            mixer.music.play()
            guess = input("What was the word? ")
            if guess == readable_data or guess == readable_data.lower():
                print("Correct! \n")
                score += 1
            elif guess == "repeat" or guess == "Repeat":
                guess_word()
            else:
                print(f"Wrong! The word was {readable_data} \n")
        guess_word()
    for i in range(10):
        game()
    print(f"\n\nYou scored {score}/10")

    # return returnInt
if __name__ == '__main__':
    main()
