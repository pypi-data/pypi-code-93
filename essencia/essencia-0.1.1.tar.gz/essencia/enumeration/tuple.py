"""Tuple type enum"""

__all__=[
    'Month',

]

from enum import Enum
from collections import namedtuple

from essencia.enumeration.abstract import TupleEnum


MonthTuple = namedtuple("MonthTuple", "integer usn brn abbr")


class Month(MonthTuple, Enum):
    JAN = MonthTuple(1, "January", "Janeiro", "Jan")
    FEB = MonthTuple(2, "February", "Fevereiro", "Fev")
    MAR = MonthTuple(3, "March", "Março", "Mar")
    APR = MonthTuple(4, "April", "Abril", "Abr")
    MAY = MonthTuple(5, "May", "Maio", "Mai")
    JUN = MonthTuple(6, "June", "Junho", "Jun")
    JUL = MonthTuple(7, "July", "Julho", "Jul")
    AUG = MonthTuple(8, "August", "Agosto", "Ago")
    SEP = MonthTuple(9, "September", "Setembro", "Set")
    OCT = MonthTuple(10, "October", "Outubro", "Out")
    NOV = MonthTuple(11, "November", "Novembro", "Nov")
    DEZ = MonthTuple(12, "December", "Dezembro", "Dez")

    def __repr__(self):
        return f"<{type(self).__name__}(integer={self.integer}, abbr={self.abbr}, brn={self.brn}, usn={self.usn})>"

    @classmethod
    def members(cls):
        return cls.__members__

    @classmethod
    def int_map(cls):
        return {x.integer: x.brn for x in cls.values()}

    @classmethod
    def values(cls):
        return cls.members().values()

    @classmethod
    def items(cls):
        return cls.members().items()

    @classmethod
    def as_string(cls, v: int):
        return cls.int_map().get(v)


class MainInformant(TupleEnum):
    '''As informações foram fornecidas {}.'''
    PATIENT_ONLY = ('pelo paciente apenas', 'fonte: paciente;\n\n', 'Todas as informações deste registro foram concedidas pelo próprio paciente.')
    PATIENT_AND_RELATIVE = ('pelo paciente e acompanhante (familiar)', '', 'As informações deste registro foram concedidas pelo próprio paciente acompanhado por familiar.')
    RELATIVE_ONLY = ('por familiar apenas', '', 'As informações deste registro foram concedidas apenas por familiar do paciente.')
    PATIENT_AND_OTHER = ('pelo paciente e acompanhante (terceiro)', '', 'As informações deste registro foram concedidas pelo próprio paciente acompanhado por familiar.')
    OTHER_ONLY = ('por responsável (não familiar)', '', 'As informações deste registro foram concedidas por acompanhante responsável pelo paciente.' )


class Reason(TupleEnum):
    START_TREATMENT = ('iniciar tratamento', 'com finalidade de iniciar tratamento', 'O motivo principal da entrevista é iniciar tratamento.')
    REVISION = ('revisão de tratamento', 'com finalidade de revisão de caso', 'A entrevista atual tem como finalidade revisão de tratamento.')
    DOCUMENTATION = ('documentação do caso clínico', 'com finalidade de documentação de caso', 'A entrevista atual tem como finalidade registro e documentação de caso clínico.')


class VisitType(TupleEnum):
    FIRST_VISIT = ('Visita Inicial', '', 'Visita Inicial.')


class Start(TupleEnum):
    ACUTE = ('agudo', 'apresentação inicial aguda', 'A apresentação inicial do episódio foi aguda.')
    SUBACUTE = ('subagudo', 'de apresentação inicial subaguda', 'A apresentação inicial do episódio foi subaguda.')
    INSIDIOUS = ('insidioso', 'de apresentação inicial insidiosa', 'O quadro teve início de forma insidiosa, com piora progressiva ao longo do tempo.')
    INTERMITTENT = ('intermitente', 'de apresentação inicial intermitente', 'Os sintomas iniciaram de forma intermitente, com crises intercaladas com períodos de melhora.')


class Evolution(TupleEnum):
    RECURRENT = ('recorrente', 'de evolução recorrente (remissão e recorrência)', 'A evolução foi recorrente, com períodos de remissão intercrise.')
    REMITTED = ('remissão', 'evoluindo para remissão', 'Após a apresentação inicial o quadro evoluiu para remissão dos sintomas.')
    PERSISTENT = ('persistente', 'evoluindo com persistência do quadro', 'O quadro evoluiu de maneira persistente, sem melhora dos sintomas desde a apresentação inicial.')
    OSCILLATING = ('oscilante', 'evoluindo de sintomas oscilantes', 'De evolução oscilante, descreve persistência das queixas mais ou menos intensas ao longo do tempo.')


class EpisodeDuration(TupleEnum):
    MINUTES = ('minutos', 'duração de minutos', 'Um episódio tem duração de alguns minutos.')
    HOURS = ('horas', 'duração de horas', 'O episódio teve duração de horas.')
    DAYS = ('dias', 'duração de dias', 'Um episódio tem duração de dias.')
    WEEKS = ('semanas', 'duração de semanas', 'Um episódio tem duração de semanas.')
    MONTHS = ('meses', 'duração de meses', 'Um episódio tem duração de meses.')
    YEARS = ('anos', 'duração de anos', 'Um episódio tem duração de anos.')


class CurrentTherapy(TupleEnum):
    REGULAR = ('regulra', '', 'Refere suporte psicoterápico regular e estável.')
    NOT_REGULAR = ('irregular', '', 'Não segue a psicoterapia de forma regular.')
    REFUSE = ('recusa', '', 'Recusa qualquer tipo de acompanhamento psicológico.')


class CurrentState(TupleEnum):
    SEVERE = ('severa', 'de evolução recorrente (remissão e recorrência)', 'A evolução foi recorrente, com períodos de remissão intercrise.')
    MODERATE = ('moderada', 'evoluindo para remissão', 'Após a apresentação inicial o quadro evoluiu para remissão dos sintomas.')
    MILD = ('leve', 'evoluindo com persistência do quadro', 'O quadro evoluiu de maneira persistente, sem melhora dos sintomas desde a apresentação inicial.')
    ABSENT = ('ausente', 'evoluindo de sintomas oscilantes', 'A evolução foi oscilante, com períodos de melhora parcial e outros mais intensos.')


class PharmacotherapyEfficacy(TupleEnum):
    '''O tratamento é considerado {} para controle da apresentação clínica.'''
    EFFECTIVE = ('eficaz', '', 'A medicação é eficaz.')
    MODERATE_EFFICACY = ('parcialmente eficaz', '', 'A medicação é moderadamente eficaz')
    MILD_EFFICACY = ('pouco eficaz', '', 'A medicação é pouco eficaz')
    INEFFECTIVE = ('ineficaz', '', 'A medicação é ineficaz')


class PharmacotherapyTolerability(TupleEnum):
    '''Quando a eventos adversos reporta que a medicação é de forma geral {}.'''
    TOLERABLE = ('bem tolerada', '', 'A tolerância farmacológica é excelente, sem queixa quanto a eventos adversos.')
    MODERATE_TOLERABILITY = ('parcialmente tolerada', '', 'Apresenta alguns efeitos colarais mas no geral tolera bem a farmacoterapia.')
    MILD_TOLERABILITY = ('pouco tolerada', '', 'Apresenta eventos adversos que dificultam o tratamento farmacológico.')
    NOT_TOLERABLE = ('não tolerada', '', 'Reporta não tolerar a medicação, sendo a descontinuação necessária.')


class PharmacotherapyAffordability(TupleEnum):
    '''A medicação é {} do ponto de vista financeiro.'''
    AFFORDABLE = ('acessível', '', 'O tratamento farmacológico é acessível para o paciente.')
    MODERATE_AFFORDABILITY = ('parcialmente acessível', '', 'O tratamento farmacológico é parcialmente acessível para o paciente.')
    MILD_AFFORDABILITY = ('pouco acessível', '', 'O tratamento farmacológico é pouco acessível para o paciente.')
    UNAFFORDABLE = ('inacessível', '', 'O tratamento farmacológico atual é inacessível para o paciente.')


class ReportType(TupleEnum):
    '''Documento do tipo {}.'''
    MEDICAL_REPORT = ('Relatório Médico', '', 'Relatório médico')
    MEDICAL_LICENCE = ('Licença Médica', '', 'Atestado Médico')
    TREATMENT_ATTENDANCE = ('Atestado de Comparecimento', '', 'Atestado de Comparecimento')


class CurrentIncapacity(TupleEnum):
    '''A incapacidade atual é do tipo {}.'''
    TOTAL_PERMANENT = ('permanente e total', '', 'A incapacidade atual é considerada total e permanente.')
    TOTAL_TEMPORARY = ('temporária porém total', '', 'A incapacidade atual é considerada total porém temporária, com expectativa de recuperação.')
    PARTIAL_PERMANENT = ('parcial porém permanente', '', 'A incapacidade atual é considerada parcial porém permanente.')
    PARTIAL_TEMPORARY = ('parcial e temporária', '', 'A incapacidade atual é parcial e temporária, com expectativa de recuperação funcional.')


class MedicationAdherence(TupleEnum):
    FULL_ADHERENCE = ('total', '', 'A aderência à prescrição é total.')
    GOOD_ADHERENCE = ('boa', '', 'A aderência ao tratamento é boa, com falhas ocasionais.')
    PARTIAL_ADHERENCE = ('parcial', '', 'Faz uso parcial das medicações recomendadas, aproximadamente metade do prescrito.')
    POOR_ADHERENCE = ('ruim', '', 'A aderência à prescrição é muito reduzida.')
    NO_ADHERENCE= ('ausente', '', 'Não faz uso da prescrição recomendada.')


class ClinicalStability(TupleEnum):
    STABLE = ('estável', '', 'O quadro atual é considerado estável.')
    UNSTABLE = ('instável', '', 'O quadro atual sugere apresentação instável.')


class DiseaseActivity(TupleEnum):
    ACTIVE = ('ativa', '', 'Apresentação clínica atual com sintomas presentes e indicativo de doença ativa.')
    INTERMITTENT = ('intermitente', '', 'Apresentação atual do tipo intermitente, com períodos de sintomas intercalados com fases de normalidade.')
    RESIDUAL = ('residual', '', 'Apresentação atual do tipo residual, com controle de fase aguda persistindo sintomas residuais.')
    ABSENT = ('ausente', '', 'Apresentação clínica prévia em remissão.')

