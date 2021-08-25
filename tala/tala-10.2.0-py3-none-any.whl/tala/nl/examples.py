# coding: utf-8
import csv
import os

from jinja2 import Template

from tala.model import sort
from tala.nl.languages import ENGLISH, SWEDISH, SPANISH, PERSIAN

SUPPORTED_BUILTIN_SORTS = [sort.INTEGER, sort.DATETIME, sort.PERSON_NAME, sort.STRING]


class SortNotSupportedException(Exception):
    pass


class Examples(object):
    def __init__(self, language_code, custom_entity_examples, lookup_data):
        self._language_code = language_code
        self._custom_entity_examples = custom_entity_examples
        self._load_builtin_sort_examples_from_csv()
        self._load_custom_sort_examples_from_csv()
        self._load_lookup_data_from_csv(lookup_data)

    def _load_builtin_sort_examples_from_csv(self):
        self._builtin_sort_examples = {
            sort_name: self._load_examples_from_csv(sort_name)
            for sort_name in SUPPORTED_BUILTIN_SORTS
        }

    def _load_examples_from_csv(self, sort_name):
        def default_path():
            dirname = os.path.dirname(os.path.abspath(__file__))
            return f"{dirname}/entity_examples/{self._language_code}/{sort_name}.csv"

        if sort_name in self._custom_entity_examples:
            path = self._custom_entity_examples[sort_name]
        else:
            path = default_path()
        return self._load_lines_from_csv(path)

    def _load_lookup_data_from_csv(self, data):
        self._lookup_data = {}
        for sort_name in data:
            path = data[sort_name]
            self._lookup_data[sort_name] = self._load_lines_from_csv(path)

    def _load_lines_from_csv(self, path):
        with open(path) as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=["value"])
            lines = [row["value"] for row in reader]
            return lines

    def _load_custom_sort_examples_from_csv(self):
        self._custom_sort_entity_examples = {}
        for sort_name in self._custom_entity_examples:
            if sort_name not in SUPPORTED_BUILTIN_SORTS:
                path = self._custom_entity_examples[sort_name]
                self._custom_sort_entity_examples[sort_name] = self._load_lines_from_csv(path)

    @property
    def negative(self):
        raise NotImplementedError()

    @property
    def integer(self):
        raise NotImplementedError()

    @property
    def string(self):
        raise NotImplementedError()

    @property
    def datetime(self):
        raise NotImplementedError()

    @property
    def person_name(self):
        raise NotImplementedError()

    @property
    def yes(self):
        raise NotImplementedError()

    @property
    def no(self):
        raise NotImplementedError()

    @property
    def yes_strict(self):
        return self.yes[0]

    @property
    def no_strict(self):
        return self.no[0]

    @property
    def top(self):
        raise NotImplementedError()

    @property
    def up(self):
        raise NotImplementedError()

    @property
    def how(self):
        raise NotImplementedError()

    @property
    def done(self):
        raise NotImplementedError()

    @property
    def negative_perception(self):
        raise NotImplementedError()

    @property
    def negative_acceptance(self):
        raise NotImplementedError()

    @property
    def answer_templates(self):
        yield Template('{{ name }}')

    @property
    def answer_negation_templates(self):
        raise NotImplementedError()

    @property
    def lookup_data(self):
        return self._lookup_data

    @property
    def custom_sort_entity_examples(self):
        return self._custom_sort_entity_examples

    def get_builtin_sort_examples(self, sort):
        if sort.is_domain_sort() or sort.is_boolean_sort():
            return []
        if sort.get_name() in SUPPORTED_BUILTIN_SORTS:
            return self._builtin_sort_examples[sort.get_name()]
        raise SortNotSupportedException(f"Builtin sort '{sort.get_name()}' is not yet supported together with RASA")

    @staticmethod
    def from_language(language_code, custom_entity_examples_for_builtin_sorts, lookup_data):
        examples_classes = {
            ENGLISH: EnglishExamples,
            SWEDISH: SwedishExamples,
            SPANISH: SpanishExamples,
            PERSIAN: PersianExamples
        }
        examples_class = examples_classes[language_code]
        return examples_class(language_code, custom_entity_examples_for_builtin_sorts, lookup_data)


class EnglishExamples(Examples):
    @property
    def negative(self):
        phrases = [
            "aboard", "about", "above", "across", "after", "against", "along", "among", "as", "at", "on", "atop",
            "before", "behind", "below", "beneath", "beside", "between", "beyond", "but", "by", "come", "down",
            "during", "except", "for", "from", "in", "inside", "into", "less", "like", "near", "of", "off", "on",
            "onto", "opposite", "out", "outside", "over", "past", "save", "short", "since", "than", "then", "through",
            "throughout", "to", "toward", "under", "underneath", "unlike", "until", "up", "upon", "with", "within",
            "without", "worth", "is", "it", "the", "a", "am", "are", "them", "this", "that", "I", "you", "he", "she",
            "they", "them", "his", "her", "my", "mine", "their", "your", "us", "our"
        ]
        question_phrases = [
            "how", "how's", "how is", "how's the", "how is the", "when", "when's", "when is", "when is the",
            "when's the", "what", "what is", "what's", "what's the", "what is the", "why", "why is", "why's",
            "why is the", "why's the"
        ]
        action_phrases = [
            "do", "make", "tell", "start", "stop", "enable", "disable", "raise", "lower", "decrease", "increase", "act",
            "determine", "say", "ask", "go", "shoot", "wait", "hang on", "ok", "show", "help"
        ]
        for phrase in phrases:
            yield phrase
        for phrase in question_phrases:
            yield phrase
        for phrase in action_phrases:
            yield phrase

    @property
    def integer(self):
        return self._integer_examples

    @property
    def yes(self):
        return [
            "yes", "yeah", "yep", "sure", "ok", "of course", "very well", "fine", "right", "excellent", "okay",
            "perfect", "I think so"
        ]

    @property
    def no(self):
        return [
            "no", "nope", "no thanks", "no thank you", "negative", "don't want to", "don't", "do not", "please don't"
        ]

    @property
    def top(self):
        return [
            "forget it", "never mind", "get me out of here", "start over", "beginning", "never mind that", "restart"
        ]

    @property
    def up(self):
        return [
            "go back", "back", "previous", "back to the previous", "go to the previous", "go back to the previous one"
        ]

    @property
    def how(self):
        return [
            "how do I do that", "how", "can you tell me how to do that", "I don't know how should I do that",
            "how can I do that"
        ]

    @property
    def done(self):
        return [
            "I'm done", "done", "ready", "it's ready", "I'm ready", "completed", "check", "I have finished", "finished",
            "done and done", "it's done now", "okay next", "next", "next instruction"
        ]

    @property
    def negative_perception(self):
        return [
            "repeat",
            "repeat it",
            "repeat that",
            "pardon",
            "sorry",
            "can you repeat that",
            "excuse me",
            "what was that",
            "what did you say",
            "come again",
        ]

    @property
    def negative_acceptance(self):
        return ["I don't know", "I don't know that", "it doesn't matter"]

    @property
    def answer_negation_templates(self):
        yield Template('not {{ name }}')

    @property
    def thank_you(self):
        return [
            "thank you",
            "thank you very much",
            "thanks",
            "big thanks",
            "thanks a lot",
        ]

    @property
    def greeting(self):
        return [
            "hello",
            "hi",
            "good day",
            "what's up",
            "good evening",
            "good morning",
            "hey",
        ]


class SwedishExamples(Examples):
    @property
    def negative(self):
        phrases = [
            "om", "ovanför", "tvärsöver", "efter", "mot", "bland", "runt", "som", "på", "vid", "ovanpå", "före",
            "bakom", "nedan", "under", "bredvid", "mellan", "bortom", "men", "av", "trots", "ner", "förutom", "för",
            "från", "i", "inuti", "in i", "nära", "nästa", "mittemot", "ut", "utanför", "över", "per", "plus", "runt",
            "sedan", "än", "genom", "tills", "till", "mot", "olik", "upp", "via", "med", "inom", "utan", "är", "vara",
            "den", "det", "en", "ett", "dem", "denna", "detta", "jag", "du", "ni", "han", "hon", "hen", "de", "hans",
            "hennes", "hens", "min", "mina", "deras", "er", "din", "vi", "oss", "vår"
        ]
        question_phrases = ["hur", "hur är", "när", "när är", "vad", "vad är", "varför", "varför är"]
        action_phrases = [
            "gör", "göra", "skapa", "berätta", "tala om", "börja", "starta", "sluta", "stopp", "stanna", "sätt på",
            "stäng av", "höj", "sänk", "öka", "minska", "agera", "bestäm", "säg", "fråga", "gå", "kör", "vänta", "ok",
            "visa", "hjälp"
        ]
        for phrase in phrases:
            yield phrase
        for phrase in question_phrases:
            yield phrase
        for phrase in action_phrases:
            yield phrase

    @property
    def yes(self):
        return [
            "ja", "javisst", "japp", "absolut", "det stämmer", "precis", "självklart", "varför inte", "ok", "okej",
            "det blir kanon", "perfekt", "det skulle jag tro", "ja tack"
        ]

    @property
    def no(self):
        return [
            "nej", "nix", "nähe du", "icke", "nej tack", "helst inte", "det vill jag inte", "det tror jag inte",
            "det skulle jag inte tro", "gör inte det", "gör det inte"
        ]

    @property
    def top(self):
        return ["glöm alltihop", "jag skiter i detta", "ta mig härifrån", "börja om", "börja från noll"]

    @property
    def up(self):
        return ["gå tillbaka", "vad var den förra", "backa", "förra", "tillbaka", "ta mig tillbaka", "backa till förra"]

    @property
    def how(self):
        return ["hur gör jag det", "hur", "kan du tala om för mig hur man gör det", "hur gör man", "hur gör man det"]

    @property
    def done(self):
        return [
            "jag är klar", "klar", "färdig", "nu är det gjort", "jag har gjort klart", "slutfört", "det var det",
            "nu är det klart", "det är färdigt", "okej nästa", "nästa", "nästa instruktion", "jag är färdig"
        ]

    @property
    def negative_perception(self):
        return [
            "ursäkta",
            "förlåt",
            "kan du repetera det",
            "repetera",
            "repetera det",
            "upprepa",
            "upprepa vad du sa",
            "vad sa du",
            "ta det en gång till",
            "va",
        ]

    @property
    def negative_acceptance(self):
        return ["jag vet inte", "jag vet inte det", "jag kan inte svara på det", "det spelar ingen roll"]

    @property
    def answer_negation_templates(self):
        yield Template('inte {{ name }}')

    @property
    def thank_you(self):
        return [
            "tack",
            "tack så mycket",
            "tackar",
        ]

    @property
    def greeting(self):
        return ["hallå", "hej", "goddag", "tjena", "godkväll", "godmorgon", "hejsan"]


class SpanishExamples(Examples):
    @property
    def negative(self):
        phrases = [
            "a bordo", "acerca de", "arriba", "a través de", "después de", "en contra", "a lo largo de", "entre",
            "como", "en", "en", "en lo alto", "antes", "detrás", "abajo", "debajo", "al lado", "entre", "más allá de",
            "pero", "por", "abajo", "durante", "excepto", "para", "desde", "en", "dentro", "en", "menos", "como",
            "cerca", "de", "encima de", "sobre", "opuesto", "fuera", "fuera de", "corto", "desde", "que", "entonces",
            "a lo largo de", "hasta", "hacia", "debajo de", "a diferencia de", "hasta", "arriba", "con", "dentro de",
            "sin", "vale", "es"
            "se", "el", "la"
            "a", "soy", "son", "ellos", "este", "ese", "yo", "usted", "él", "ella", "ellos", "ellas", "su", "sus", "mi",
            "tu", "tú", "nosotros", "nosotras", "vosotros", "vosotras", "nuestro", "nuestra", "vuestro", "vuestra",
            "vuestros", "vuestras", "mío", "mía", "míos", "mías", "tuyo", "tuyos", "tuya", "tuyas", "suyo", "suya",
            "suyos", "suyas"
        ]
        question_phrases = [
            "cómo", "cómo está", "cómo es", "cómo está el", "cómo es el", "cómo está la", "cómo es la",
            "cómo están los", "cómo están las"
            "cuándo", "cuándo es", "cuándo está", "cuándo es el", "cuándo es la", "cuándo son los", "cuándo son las",
            "cuándo está el", "cuándo está la", "cuándo están los", "cuándo están las", "qué", "qué es", "qué es la",
            "qué es el", "qué son los", "qué son las", "cuál", "cuál es", "cuál es la", "cuál es el", "cuáles son los",
            "cuáles son las", "por qué", "por qué es", "por qué está", "por qué es el", "por qué es la", "por qué son",
            "por qué son los", "por qué son las", "por qué está el", "por qué está la", "por qué están los",
            "por qué están las"
        ]
        action_phrases = [
            "hacer", "decir", "iniciar", "detener", "habilitar", "deshabilitar", "querer", "dar", "haber"
            "subir", "bajar", "disminuir", "aumentar", "actuar", "determinar", "preguntar", "ir", "disparar", "esperar",
            "esperar", "aceptar", "mostrar", "enseñar", "ayudar"
        ]
        for phrase in phrases:
            yield phrase
        for phrase in question_phrases:
            yield phrase
        for phrase in action_phrases:
            yield phrase

    @property
    def yes(self):
        return [
            "sí", "claro", "desde luego", "por supuesto", "de acuerdo", "vale", "perfecto", "bien", "okei", "sip", "sep"
        ]

    @property
    def no(self):
        return ["no", "de ningún modo", "de ninguna manera", "en absoluto", "na", "nop", "ni de broma", "para nada"]

    @property
    def top(self):
        return [
            "vuelve a empezar", "vuelve al principio", "vuelve al inicio", "principio", "inicio", "desde el principio",
            "reinicia", "empieza de nuevo", "olvídalo", "olvida todo"
        ]

    @property
    def up(self):
        return [
            "atrás", "vuelve atrás", "vuelve", "regresa", "vuelve una atrás", "quiero ir atrás", "quiero volver atrás"
        ]

    @property
    def how(self):
        return ["cómo puedo hacer eso", "cómo", "cómo lo hago", "puedes decirme cómo hacerlo", "no sé hacer eso"]

    @property
    def done(self):
        return [
            "Ya está", "listo", "completado", "hecho", "ya he acabado", "acabado", "ya está listo", "ya estoy",
            "ya está hecho"
        ]

    @property
    def negative_perception(self):
        return [
            "repite",
            "puedes repetir",
            "repite por favor",
            "otra vez",
            "dilo otra vez",
            "qué",
            "cómo",
            "cómo has dicho",
            "qué has dicho",
        ]

    @property
    def negative_acceptance(self):
        return ["yo no sé", "no sé eso", "no puedo contestar eso", "no importa"]

    @property
    def answer_negation_templates(self):
        yield Template('no {{ name }}')

    @property
    def thank_you(self):
        return ["gracias", "muchas gracias", "muchísimas gracias", "mersi"]

    @property
    def greeting(self):
        return ["buenas", "hola", "buenas noches", "buenos días"]


class PersianExamples(Examples):
    @property
    def negative(self):
        phrases = [
            "داخل", "درباره", "بالا", "در سراسر", "بعد", "علیه", "همراه", "در بین", "به عنوان", "در", "روی", "بالای",
            "قبل", "پشت", "زیر", "زیر", "کنار", "بین", "فراتر", "اما", "توسط", "بیا", "پایین", "هنگام", "به جز", "برای",
            "از", "در", "داخل", "به", "کمتر", "مانند", "نزدیک", "از", "خاموش", "روشن", "روی", "مخالف", "خارج", "بیش",
            "گذشته", "ذخیره", "کوتاه", "از", "بعد", "از طریق", "سراسر", "به", "به سمت", "زیر", "بر خلاف", "تا", "بالا",
            "بر", "با", "بدون", "ارزش", "است", "آن", "این", "یک", "من", "هستند", "آنها", "این", "آن", "من", "شما", "او",
            "آنها", "ایشان", "او", "اون", "مال", "آنها", "شما", "ما"
        ]
        question_phrases = [
            "چگونه", "چطور", "چه وقت", "چه وقتی", "برای چه", "وقتی", "چه زمانی", "چه موقع", "کی"
            "چه زمانی", "چه", "برای چی", "چطور میشه که", "چی میشه که", "برای چه", "چرا"
        ]
        action_phrases = [
            "انجام بده", "بساز", "بگو", "شروع کن", "متوقف کن", "فعال کن", "غیرفعال کن", "افزایش بده", "پایین بیار",
            "کاهش بده", "افزایش بده", "عمل کن", "تعیین کن", "بگو", "سؤال کن", "برو", "شلیک کن", "صبر کن", "متوقف شو",
            "نشون بده", "نمایش بده", "کمک کن"
        ]
        for phrase in phrases:
            yield phrase
        for phrase in question_phrases:
            yield phrase
        for phrase in action_phrases:
            yield phrase

    @property
    def yes(self):
        return [
            "بله", "آره", "مطمئن", "مطمئنم", "اوکی", "البته", "خیلی خوب", "خوبه", "درست", "درسته", "عالی", "عالیه",
            "من اینطور فکر میکنم"
        ]

    @property
    def no(self):
        return ["نه", "نه متشکرم", "نه ممنون", "نه خیلی ممنون", "منفی", "اینو نمیخوام", "نیمخوام", "نکن", "لطفا نکن"]

    @property
    def top(self):
        return [
            "فراموش کن", "ولش کن", "منو از اینجا بیرون ببر", "دوباره شورع کن", "ابتدا", "اینو ولش کن", "شروع دوباره"
        ]

    @property
    def up(self):
        return ["برو عقب", "عقب", "قبلی", "برو به عقب", "برو به قبلی", "قبلیه"]

    @property
    def how(self):
        return ["چطور این کار را انجام دهم"]

    @property
    def done(self):
        return [
            "من تمام شدم",
            "انجام شده",
            "تکمیل شده",
            "بررسی",
            "من تمام کرده ام",
            "تمام شده",
            "انجام شده و انجام شده",
            "الان تمام شده",
        ]

    @property
    def negative_perception(self):
        return [
            "تکرار",
            "تکرار کن",
            "تکرار کنید",
            "بخشش",
            "متاسف",
            "آیا می توانید آن را تکرار کنید؟",
            "ببخشید",
            "آن چه بود",
            "چی گفتی",
            "دوباره بیا",
        ]

    @property
    def negative_acceptance(self):
        return ["نمی دانم", "من نمی دانم که", "من نمی توانم پاسخ دهم", "مهم نیست"]

    @property
    def answer_negation_templates(self):
        yield Template('not {{ name }}')

    @property
    def thank_you(self):
        return [
            "با تشکر",
            "خیلی ممنون",
        ]

    @property
    def greeting(self):
        return [
            "خدمت",
            "سلام",
            "صبح بخیر",
            "عصر بخیر",
        ]
