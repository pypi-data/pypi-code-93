"""All commonly used pydantic questionnaire dataclasses ready for reuse."""

from typing import Literal
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, validator, conint, condecimal


class Wellbeing(BaseModel):
    """Questionnaire regarding to the wellbeing of the participant."""

    q_start: datetime
    q_end: datetime
    well_0: conint(ge=0, le=3)
    well_1: conint(ge=0, le=3)
    well_2: conint(ge=0, le=3)
    well_3: conint(ge=0, le=3)
    well_4: conint(ge=0, le=3)
    well_5: conint(ge=0, le=3)
    well_6: conint(ge=0, le=3)
    well_7: conint(ge=0, le=3)
    well_8: conint(ge=0, le=3)
    well_9: conint(ge=0, le=3)
    well_10: conint(ge=0, le=3)
    well_11: conint(ge=0, le=3)
    well_12: conint(ge=0, le=3)
    well_13: conint(ge=0, le=3)
    well_14: conint(ge=0, le=3)

    @property
    def score(self):
        """Calculate score of questionnaire."""
        return sum([getattr(self, "well_" + str(i)) for i in range(15)]) / 45


class Mobility(BaseModel):
    """Short questionnaire regarding mobility of participant."""

    q_start: datetime
    q_end: datetime
    mob0: conint(ge=0, le=2)
    mob_freq0: conint(ge=0, le=3)
    mob_indep0: conint(ge=0, le=2)
    mob1: conint(ge=0, le=2)
    mob_freq1: conint(ge=0, le=3)
    mob_indep1: conint(ge=0, le=2)
    mob2: conint(ge=0, le=2)
    mob_freq2: conint(ge=0, le=3)
    mob_indep2: conint(ge=0, le=2)
    mob3: conint(ge=0, le=2)
    mob_freq3: conint(ge=0, le=3)
    mob_indep3: conint(ge=0, le=2)
    mob4: conint(ge=0, le=2)
    mob_freq4: conint(ge=0, le=3)
    mob_indep4: conint(ge=0, le=2)

    @property
    def score(self):
        """Calculate score of questionnaire."""
        m_map = {0: 1, 1: 0.5, 2: 0}
        mi_map = {0: 1, 1: 1.5, 2: 2}

        m = [getattr(self, "mob" + str(i)) for i in range(5)]
        mf = [getattr(self, "mob_freq" + str(i)) for i in range(5)]
        mi = [getattr(self, "mob_indep" + str(i)) for i in range(5)]

        return sum([(i + 1) * m_map[m[i]] * (mf[i] + 1) * mi_map[mi[i]]
                     for i in range(5)])


class Loneliness(BaseModel):
    """Loneliness questionnaire answers.
    
    Data is structures in a few categories to find them easier, the following prefixes are defined:
    
    q => metadata about questionnaire (e.g., timestamps)
    
    l => loneliness questions

    Parameters
    ----------
    BaseModel : pydantic.BaseModel
        Pydantic base dataclass

    Returns
    -------

    """

    q_start: datetime
    q_end: datetime
    l_0: conint(ge=0, le=2)
    l_1: conint(ge=0, le=2)
    l_2: conint(ge=0, le=2)
    l_3: conint(ge=0, le=2)
    l_4: conint(ge=0, le=2)
    l_5: conint(ge=0, le=2)
    l_6: conint(ge=0, le=2)
    l_7: conint(ge=0, le=2)
    l_8: conint(ge=0, le=2)
    l_9: conint(ge=0, le=2)
    l_10: conint(ge=0, le=2)

    @property
    def emo_l(self):
        """Calculate emotional loneliness score."""
        emotional_items = [1, 2, 4, 5, 8, 9]
        return sum([
            1 for q in emotional_items
            if getattr(self, "l_" + str(q)) in [0, 1]
        ])

    @property
    def soc_l(self):
        """Calculate social loneliness score."""
        social_items = [0, 3, 6, 7, 10]
        return sum([
            1 for q in social_items if getattr(self, "l_" + str(q)) in [1, 2]
        ])

    @property
    def tot_l(self):
        """Calculate total loneliness score."""
        return self.emo_l + self.soc_l

    @validator('q_start', "q_end", pre=True)
    def time_validate(cls, v):
        """Make sure that the date type formatting works out.

        Parameters
        ----------
        v :
            

        Returns
        -------

        """
        return datetime.fromisoformat(v)


class Topics(BaseModel):
    """Topics questionnaire answers.
    
    Data is structures in a few categories to find them easier the following prefixes are defined:
    
    q => metadata about questionnaire (e.g., timestamps)
    
    v => questions about your feeling (voelen)
    
    l => questions about physical attributes (lichamelijk)
    
    p => questions about practical activities (praktisch)
    
    m => questions about the mouth (mond)
    
    z => questions about diseases (ziekte)

    Parameters
    ----------
    BaseModel : pydantic.BaseModel
        Pydantic base dataclass

    Returns
    -------

    """

    q_start: datetime
    q_end: datetime
    s_soc_act: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_zenuw: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_somber: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_put: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_kalm: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_gelukkig: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_pijn: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_angst: condecimal(multiple_of=Decimal('0.2'), le=1)
    v_kw_leven: condecimal(multiple_of=Decimal('0.1'), le=1)
    l_lopen: condecimal(multiple_of=Decimal('0.2'), le=1)
    l_geheugen: conint(ge=0, le=1)
    l_gevallen: conint(ge=0, le=1)
    p_wassen_aankleden: condecimal(multiple_of=Decimal('0.2'), le=1)
    p_dagelijkse_act: condecimal(multiple_of=Decimal('0.2'), le=1)
    p_kleden: Literal[0, 0.33, 0.66, 1]
    p_stoel: Literal[0, 0.33, 0.66, 1]
    p_afdrogen: Literal[0, 0.33, 0.66, 1]
    p_trap: Literal[0, 0.33, 0.66, 1]
    p_rondlopen: Literal[0, 0.33, 0.66, 1]
    p_voet: Literal[0, 0.33, 0.66, 1]
    p_huishouden: Literal[0, 0.33, 0.66, 1]
    p_boodschap: Literal[0, 0.33, 0.66, 1]
    p_medicijnen: Literal[0, 0.33, 0.66, 1]
    p_vervoer: Literal[0, 0.33, 0.66, 1]
    m_pijn: Literal[0, 0.25]
    m_kauw: Literal[0, 0.25]
    m_droog: Literal[0, 0.25]
    m_slik: Literal[0, 0.25]
    z_suikerziekte: Literal[0, 1]
    z_beroerte: Literal[0, 1]
    z_hartfalen: Literal[0, 1]
    z_kanker: Literal[0, 1]
    z_astma: Literal[0, 1]
    z_urineverlies: Literal[0, 1]
    z_gewrichtsslijtage: Literal[0, 1]
    z_gewrichtsontsteking: Literal[0, 1]
    z_botontkalking: Literal[0, 1]
    z_botbreuken: Literal[0, 1]
    z_duizeligheid: Literal[0, 1]
    z_parkinson: Literal[0, 1]
    z_depressie: Literal[0, 1]
    z_paniekstoornis: Literal[0, 1]
    z_dementie: Literal[0, 1]
    z_gehoorproblemen: Literal[0, 1]
    z_zien: Literal[0, 1]

    @property
    def frailty_index(self):
        """Calculate frailty based on TOPICS questionnaire."""
        return round(
            sum([float(v)
                 for k, v, in self.__dict__.items() if k[0] != "q"]) / 42.0, 3)

    @validator('q_start', "q_end", pre=True)
    def time_validate(cls, v):
        """Make sure that the date type formatting works out.

        Parameters
        ----------
        v :
            

        Returns
        -------

        """
        return datetime.fromisoformat(v)
