# -*- coding: utf-8 -*-
"""Interfaces for InspectionViewer stuff."""
from .py23 import win1251


class Error(Exception):
    """IV exception."""

    pass


class ObjectClass:
    """Classes of csv objects."""

    WELD = 0
    MARKER = 1
    DEFEKT = 2
    THICK = 3
    HOR_WELD = 4
    PIPELINE_CATEGORY = 5


class TypeMarker:
    """Types of marker."""

    VALVE = 0
    MARKER = 1
    MAGNET = 2
    OTVOD = 3
    TROYNIK = 4
    CASE_START = 5
    CASE_END = 6
    REPAIR = 7
    LOAD = 8
    TURN_START = 9
    TURN_END = 10
    FEATURE = 11
    CURVE_SECTION = 12
    TURN_SEGMENT = 13


class TypeDefekt:
    """Types of defekt."""

    CORROZ = 0
    MECHANIC = 1
    DENT = 2
    DENT_METAL_LOSS = 3
    GOFRA = 4
    GWAN = 5
    TECHNOLOGY = 6
    FACTORY = 7
    ADDITIONAL_METAL = 8
    OTHER = 9
    CRACKS_HOR = 10
    CRACK_LIKE = 11
    CRACK_WELD = 12
    LAMINATION = 13
    ANOMALY_HOR_WELD = 14
    ANOMALY_SPIRAL_WELD = 15
    ELLIPSE = 16
    PODZHIG = 17
    GRINDING = 18


class TypeHorWeld:
    """Types of horizontal weld."""

    HORIZONTAL = 0
    SECOND = 1
    NO_WELD = 2
    SPIRAL = 3
    UNKNOWN = 4


class DefektSide:
    """Types of defekt location."""

    UNKNOWN = 0
    OUTSIDE = 1
    INSIDE = 2
    IN_WALL = 3


COMMON = {
  ObjectClass.WELD: win1251("Шов"),
  ObjectClass.THICK: win1251("Изменение толщины стенки трубы"),
  ObjectClass.PIPELINE_CATEGORY: win1251("Категория трубопровода"),
}

SEAM = {
  TypeHorWeld.HORIZONTAL: win1251("Продольный шов"),
  TypeHorWeld.SECOND: win1251("Двойной прод. шов"),
  TypeHorWeld.NO_WELD: win1251("Цельнотянутая труба"),
  TypeHorWeld.SPIRAL: win1251("Спиральный шов"),
  TypeHorWeld.UNKNOWN: win1251("Не определено"),
}

LINEOBJ = {
  TypeMarker.VALVE: win1251("Кран"),
  TypeMarker.MARKER: win1251("Маркер"),
  TypeMarker.MAGNET: win1251("Маркер магнитный"),
  TypeMarker.OTVOD: win1251("Отвод-врезка"),
  TypeMarker.TROYNIK: win1251("Тройник"),
  TypeMarker.CASE_START: win1251("Патрон начало"),
  TypeMarker.CASE_END: win1251("Патрон конец"),
  TypeMarker.REPAIR: win1251("Место ремонта"),
  TypeMarker.LOAD: win1251("Пригруз"),
  TypeMarker.TURN_START: win1251("Отвод (поворот) начало"),
  TypeMarker.TURN_END: win1251("Отвод (поворот) конец"),
  TypeMarker.FEATURE: win1251("Особенность"),
  TypeMarker.CURVE_SECTION: win1251("Гнутая секция"),
  TypeMarker.TURN_SEGMENT: win1251("Сегмент поворота"),
}

DEFEKTS = {
  TypeDefekt.CORROZ: win1251("Коррозия"),
  TypeDefekt.MECHANIC: win1251("Мех. повреждение"),
  TypeDefekt.DENT: win1251("Вмятина"),
  TypeDefekt.DENT_METAL_LOSS: win1251("Вмятина с дефектами потери металла"),
  TypeDefekt.GOFRA: win1251("Гофра"),
  TypeDefekt.GWAN: win1251("Аномалия кольцевого шва"),
  TypeDefekt.TECHNOLOGY: win1251("Технологический дефект"),
  TypeDefekt.FACTORY: win1251("Заводской дефект"),
  TypeDefekt.ADDITIONAL_METAL: win1251("Дополнительный металл/материал"),
  TypeDefekt.OTHER: win1251("Другое"),
  TypeDefekt.CRACKS_HOR: win1251("Зона продольных трещин"),
  TypeDefekt.CRACK_LIKE: win1251("Трещиноподобный дефект"),
  TypeDefekt.CRACK_WELD: win1251("Трещина на кольцевом шве"),
  TypeDefekt.LAMINATION: win1251("Расслоение"),
  TypeDefekt.ANOMALY_HOR_WELD: win1251("Аномалия продольного шва"),
  TypeDefekt.ANOMALY_SPIRAL_WELD: win1251("Аномалия спирального шва"),
  TypeDefekt.ELLIPSE: win1251("Эллипсность"),
  TypeDefekt.PODZHIG: win1251("Поджиг"),
  TypeDefekt.GRINDING: win1251("Зашлифовка"),
}

DEFAULT_MARKERS = [
  TypeMarker.VALVE,
  TypeMarker.MARKER,
  TypeMarker.MAGNET,
]
