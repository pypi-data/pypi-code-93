from plover.translation import Translator
from plover.steno import Stroke


def prev_page(translator: Translator, stroke: Stroke, argument: str):
    translator.next_stroke_state = "prev_page"


def next_page(translator: Translator, stroke: Stroke, argument: str):
    translator.next_stroke_state = "next_page"


def next_stroke_reload(translator: Translator, stroke: Stroke, argument: str):
    translator.next_stroke_state = "next_stroke_reload"
