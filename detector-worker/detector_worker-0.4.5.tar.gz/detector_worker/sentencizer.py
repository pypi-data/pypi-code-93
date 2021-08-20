# import spacy


# class SpacySentencizer:
#     def __init__(self):
#         spacy.cli.download('en_core_web_sm')
#         self.model = spacy.load('en_core_web_sm', disable=['ner'])

#     def split_into_sentences(self, text):
#         sentences = [(str(s).strip(), s.start_char, s.end_char) for s in self.model(text).sents]
#         return sentences


# if __name__ == "__main__":
#     sentecizer = SpacySentencizer()
#     print("Test split into sentences (Spacy)\n")
#     texts = [
#         "Enclosed areas (wet or dry), loading / handling crushed material (rocks, gravel 2-100 mm etc.) e.g. mining or quarry - like environments.",
#         "In comparison with the 120A alternator, the higher efficiency enables the 150A alternator to give approximately 20 % better output at low speeds and approximately 2 % better efficiency in delivered energy.",
#         "Once the needle has been completely withdrawn the switch (red) can be pushed forward to close off the cannula. Connect the extension lines or monitoring kits.Secure the cannula with a sterile dressing.",
#         "Entries must be at least 3,800 characters in length (including spaces)",
#         "I am a boy.My name is Gunvant",
#         "I downloaded Setup.XYZ file from the web.",
#         "Application settings are encrypted at rest and transmitted over an encrypted channel. You can choose to display them in plain text in your browser by using the controls below. Application Settings are exposed as environment variables for access by your application at runtime.",
#     ]

#     for text in texts:
#         print(text)
#         for sentence in sentecizer.split_into_sentences(text):
#             print(sentence)
#         print()
#     print()