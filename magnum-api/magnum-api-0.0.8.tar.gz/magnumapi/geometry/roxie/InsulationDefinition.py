from dataclasses import dataclass

from magnumapi.geometry.roxie.Definition import Definition


@dataclass
class InsulationDefinition(Definition):
    """Class for insulation definition.

       Attributes:
           thickness (float): The thickness (mm) on narrow side of cable
           width (float): The width (mm) on broad side of cable.

    """
    name: str
    thickness: float
    width: float
    comment: str

    @staticmethod
    def get_magnum_to_roxie_dct() -> dict:
        return {"name": "Name",
                "thickness": "Radial",
                "width": "Azimut",
                "comment": "Comment"}
