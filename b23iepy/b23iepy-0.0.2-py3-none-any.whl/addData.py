import json
import os
from __init__ import *

with open(os.path.dirname(__file__)+"/data.json", "r", encoding="utf-8") as f:
    data: dict = json.load(f)

while a := input(""):
    year, date = a.split(":")[0].split("-", 1)
    a = a.lstrip(year+"-"+date+":")
    summary, description, lang = [i.strip() for i in a.split("|")]
    date = Date.cast(date)
    if str(date) not in data:
        data[str(date)] = []
    con = False
    for i in data[str(date)]:
        if i["year"] == int(year):
            if lang not in i["data"]:
                i["data"][lang] = {
                    "summary": summary,
                    "description": description
                }
            con = True
    if con:
        continue
    data[str(date)].append(
        dict(
            year=int(year),
            data={lang: dict(summary=summary, description=description)}
        )
    )
    print(date, summary, description, lang)

with open(os.path.dirname(__file__)+"/data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
