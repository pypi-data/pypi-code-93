import csv
import json


def update_languages():
    try:
        with open("lingoshell/languages.csv", mode="r") as csv_file:
            keywords = []
            language_keywords = {}

            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                keywords.extend(list(row.values())[2:-7])

                current_language = dict(row)
                current_language.pop("AUTHOR", None)
                print(current_language)
                language_keywords[row["Language ISO 639-1 Code"]] = current_language

            with open("lingoshell/keywords.json", "w") as keywords_file:
                json.dump(keywords, keywords_file)

            with open(
                "lingoshell/language_keywords.json", "w"
            ) as language_keywords_file:
                json.dump(language_keywords, language_keywords_file)
    except Exception as e:
        print("Runtime Error:", str(e))
