# -*- coding: utf-8 -*-

import os.path

from .adaptors import JSONAdaptor, XMLAdaptor, load_from_file
from .configuration import Configurable, adopt, depends_on, document_parameters, parametrize
from .input import Unit, Value
from .parameters import BoolParameter, IntegerParameter, StringParameter, NumberParameter, FilepathParameter, \
    VectorParameter, DupletParameter, TripletParameter, PhysicalQuantityParameter, \
    ActionParameter, ChoiceParameter, ParameterGroup, ComplementaryParameterGroup, \
    SubstitutionParameterGroup, VectorParameter, TupleParameter, DupletParameter, TripletParameter

with open(os.path.join(os.path.split(__file__)[0], 'VERSION')) as fp:
    __version__ = fp.read()

del fp
del os

Bool = BoolParameter
Integer = IntegerParameter
Filepath = FilepathParameter
String = StringParameter
Number = NumberParameter
PhysicalQuantity = PhysicalQuantityParameter
Action = ActionParameter
Choice = ChoiceParameter
Group = ParameterGroup
ComplementaryGroup = ComplementaryParameterGroup
SubstitutionGroup = SubstitutionParameterGroup
Vector = VectorParameter
Tuple = TupleParameter
Duplet = DupletParameter
Triplet = TripletParameter
