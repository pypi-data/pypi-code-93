'''String type enumerations'''

from essencia.enumeration.abstract import StrEnum

# __all__=[
#     'Val',
#     'VisitType',
#     'VisitNeeds',
#     'PaymentMethod',
#     'MentalExamItem',
#     'PaymentCharge',
#     'VisitPlace'
# ]


class Val(StrEnum):
    Undefined = "Indefinido"
    Missing = "Ausente"


class VisitType(StrEnum):
    Initial = 'Inicial'
    Regular = 'Regular'
    Revision = 'Revisão'
    Revisit = 'Retorno'
    Session = 'Sessão'
    Undefined = 'Indefinido'


class VisitNeeds(StrEnum):
    MedicalCare = 'Cuidados Médicos'
    Psychotherapy = 'Psicoterapia'
    ExamResult = 'Entrega de Exames'
    Report = 'Relatório Clínico'
    Licence = 'Licença Médica'


class PaymentMethod(StrEnum):
    Cash = 'Dinheiro'
    Credit = 'Crédito'
    Debit = 'Débito'
    Check = 'Cheque'
    Transfer = 'Transferência'
    Pix = 'Pix'
    Missing = 'Nenhum'


class MentalExamItem(StrEnum):
    Mood = 'Humor'
    Affect = 'Afeto'
    Speech = 'Discurso'
    Thought = 'Pensamento'
    Motricity = 'Motricidade'


class PaymentCharge(StrEnum):
    Full = "100%"
    Half = "50%"
    No = "0%"


class VisitPlace(StrEnum):
    Telemedicine = 'Telemedicina'
    Office = 'Consultório'


class MeasureUnit(StrEnum):
    MG_PER_DECILITER = 'mg/dl'


class MedicationUnitForm(StrEnum):
    COMP = 'cp'
    CAP = 'cap'
    PATCH = 'adesivo'
    SOLUTION = 'sol'
    SYRUP = 'xarope'


class MedicationDosageForm(StrEnum):
    DROP = 'gota'
    MICRODROP = 'microgota'


class MedicationRoute(StrEnum):
    ORAL = 'via oral'
    PARENTERAL = 'via parenteral'
    TOPIC = 'via tópica'
    SUBCUTANEOUS = 'via subcutânia'
    TRANSDERMAL = 'via transdérmica'


class Gender(StrEnum):
    MALE = 'masculino'
    FEMALE = 'feminino'


class Profession(StrEnum):
    MEDICINE = 'Medicina'
    PSYCHOLOGY = 'Psicologia'
    NURSE = 'Enfermagem'


class HtmlElement(StrEnum):
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"
    SPAN = "span"
    UL = "ul"
    OL = "ol"
    LI = "li"
    DIV = "div"
    FORM = "form"
    P = "p"
    TABLE = "table"
    TR = "tr"
    TD = "td"
    TH = "th"
    BODY = "body"
    HEADER = "header"
    FOOTER = "footer"
    INPUT = "input"
    IMG = "img"
    A = 'a'
    SELECT = 'select'
    OPTION = 'option'
    HR = 'hr'


class ReportType(StrEnum):
    '''Documento do tipo {}'''
    MEDICAL_REPORT = 'Laudo Médico'
    MEDICAL_LICENCE = 'Licença Médica'
    TREATMENT_ATTENDANCE = 'Atestado de Comparecimento'


class Informant(StrEnum):
    '''As informações foram fornecidas {}'''
    PATIENT_ONLY = 'pelo paciente apenas'
    PATIENT_AND_RELATIVE = 'pelo paciente e acompanhante (familiar)'
    RELATIVE_ONLY = 'por familiar apenas'
    PATIENT_AND_OTHER = 'pelo paciente e acompanhante (terceiro)'
    OTHER_ONLY = 'por responsável (não familiar)'


class Incapacity(StrEnum):
    '''A incapacidade atual é do tipo...'''
    TOTAL_PERMANENT = 'permanente e total'
    TOTAL_TEMPORARY = 'temporária porém total'
    PARTIAL_PERMANENT = 'parcial porém permanente'
    PARTIAL_TEMPORARY = 'parcial e temporária'