from dataclasses import dataclass
@dataclass
class ObjectiveConfig:
    objective: str
    weight: float
    constraint: float

    def __str__(self):
        return "objective: %s\n" \
               "weight: %f\n" \
               "constraint: %f" % (self.objective,
                                     self.weight,
                                     self.constraint)
