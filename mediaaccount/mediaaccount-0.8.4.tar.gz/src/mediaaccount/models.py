from dataclasses import dataclass, field
from typing import List, Optional, Union
from dataclasses_json import dataclass_json, Undefined, LetterCase



@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Response:
    items: List['Article']
    next_page_link: str
    count: int

@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Article:
    source_object_id: str
    customArticle: bool
    geloescht_zeitpunkt: Optional[str]
    mediengattung_erweitert: str
    medienart_erweitert: str
    detailseiteLink: str
    id: str
    medienblattLink: str
    mediengattung: str
    medienart: str
    preview_link: str
    deeplink: str
    genre: Optional[str]
    anzeigenaequivalenzwert: Optional[float]
    gewichteterAnzeigenaequivalenzwert: Optional[float]
    isHaupttreffer: bool
    haupttrefferId: Optional[int]
    isDigitized: bool
    lieferdatum: str
    importdatum: str
    selektionsdatum: str
    erscheinungsdatum: str
    updateDatum: str
    digitalisierungsdatum: str
    tags: List[str]
    sprache: str
    herkunftsland: str
    tonalitaet: str
    auftrag: 'Auftrag'
    publikation: 'Publikation'
    inhalt: Optional['Inhalt'] = None
    medienblatt_id: Optional[str] = None
    anzahlSeiten: Optional[int] = None
    beitragslaenge: Optional[int] = None
    seite: Optional[str] = None
    positionAufSeite: Optional[str] = None
    farbigkeit: Optional[str] = None
    artikelgroesse: Optional[float] = None
    engagement: Optional['Engagement'] = None
    sendungs_beginn: Optional[str]= None
    beitragsstart: Optional[str]= None



@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Auftrag:
    auftragsnummer: int
    auftragsbeschreibung: str
    suchbegriffsname: str
    suchbegriffsId: int
    kundennummer: int
    suchbegriffsIdExtern: Optional[str]


@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Inhalt:
    headline: Optional[str]
    subheadline: Optional[str]
    abstract: Optional[str]
    text: Optional[str]
    html: Optional[str]
    previewtext: Optional[str]
    autor: Optional[str]
    previewtextWithMarking: Optional[str]
    artikeldokument: Optional[str]

@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Publikation:
    publikation_id: str
    publikationsname: str
    tvSenderName: Optional[str]
    publikations_land: str
    publizistische_einheit: Optional[int]
    reichweite: int
    bundesland: str
    werbepreis_pro_sekunde: Optional[float]
    ivw_nummer: Optional[str]
    zimpelNr: Optional[str]
    bannerpreis: Optional[float]
    bannerpreisBasis: Optional[float]
    sendungsName: Optional[str]
    ausgabennummer: str
    sprache: str
    land_name_englisch: str
    redaktion: 'Redaktion'
    verlag: 'Verlag'
    visits: Optional[int] = None
    page_impressions: Optional[int] = None
    verkaufteAuflage: Optional[int] = None
    verbreiteteAuflage: Optional[int] = None
    gedruckteAuflage: Optional[int] = None
    nielsengebiet: Optional[str] = None
    themengebiet: Optional[str] = None
    homepage: Optional[str] = None
    ivw_name_online: Optional[str] = None
    werbepreis_c1: Optional[float] = None
    werbepreis_c2: Optional[float] = None
    werbepreis_c3: Optional[float] = None
    werbepreis_c4: Optional[float] = None
    sendungslaenge: Optional[int] = None
    erscheinungszyklus: Optional[str] = None
    erscheinungszyklus_englisch: Optional[str] = None
    satzhoehe: Optional[int] = None
    satzbreite: Optional[int] = None


@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Redaktion:
    fax: str
    anrede: Optional[str] = None
    leiter: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    email: Optional[str] = None
    tel: Optional[str] = None


@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Verlag:
    name: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None

@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.PASCAL)
@dataclass
class Engagement:
    likes: int
    anzahlKommentare: int
    engagementrate: float
    engagementrate_in_prozent: float
    abrufDatum: str
    dislikes: Optional[int] = None
    shares: Optional[int] = None
    videoAufrufe: Optional[int] = None

