#
from spacy_loader import nlp

# print(nlp("در سال 5 ه.ق در ساعت 20:30 به گزارش ایسنا سمینار 30-10-1395 شیمی آلی از امروز ۱۱ شهریور ۱۳۹۶ کتابها در دانشگاه علم و صنعت ایران آغاز"
#                   " به کار کرد. این سمینار ﺆ تا ۱۳ شهریور ادامه مییابد خانم‌ها عل9یبیب *- * - 3.57 خواهدبود داشتیدمیرفتید رفتهباشد رفتهاست نرفتهباشد نرفتهبودهام نیاورید گفتن کتابهایت"
#           ))
# print("در سال 5 ه.ق در ساعت 20:30 به گزارش ایسنا سمینار 30-10-1395 شیمی آلی از امروز ۱۱ شهریور ۱۳۹۶ کتابها در دانشگاه علم و صنعت ایران آغاز"
#                   " به کار کرد. این سمینار ﺆ تا ۱۳ شهریور ادامه مییابد خانم‌ها عل9یبیب *- * - 3.57 خواهدبود داشتیدمیرفتید رفتهباشد رفتهاست نرفتهباشد نرفتهبودهام نیاورید گفتن کتابهایت")
# print(nlp.pipe_names)



with nlp.select_pipes(enable=["char_normalizer","affix2norm"]):
    print(nlp("کتابتون رو به من میدهید؟"))
nlp.remove_pipe("spell_checker")
print(nlp.pipeline)

# # nlp.to_disk("./")
# # tokenizer = nlp.tokenizer
# # tokenizer.to_disk("./tokenizer")
# # print(nlp.config.to_str())

# nlp.config.to_disk("./config.json")

#
# nlp.to_disk("./")
# nlp.config.to_disk("./config.json")