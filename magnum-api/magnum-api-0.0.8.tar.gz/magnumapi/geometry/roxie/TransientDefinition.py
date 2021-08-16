from dataclasses import dataclass

from magnumapi.geometry.roxie.Definition import Definition


@dataclass
class TransientDefinition(Definition):
    r_c: float = 0.0
    r_a: float = 0.0
    l_fil_tp: float = 0.0
    res_0: float = 0.0
    dres_over_db: float = 0.0
    f_strand_fill: float = 0.0

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "r_c": "Rc",
                "r_a": "Ra",
                "l_fil_tp": "fil.twistp.",
                "res_0": "fil.R0",
                "dres_over_db": "fil.dR/dB",
                "f_strand_fill": "strandfill.fac.",
                "comment": "Comment"}
