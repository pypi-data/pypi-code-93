"""Model for fusion class"""
import json
from pydantic import BaseModel, validator, StrictStr, StrictInt, StrictBool
from typing import Optional, List, Union
from gene.schemas import GeneDescriptor, SequenceLocation, ChromosomeLocation,\
    Extension, GeneValueObject, SimpleInterval, CytobandInterval, Location, LocationType  # noqa: E501, F401


def check_curie(cls, v):
    """Validate curies."""
    if v is not None:
        def _is_curie(value):
            """Check that value is a curie

            :param str value: Value to validate
            """
            assert all(
                [
                    value.count(':') == 1,
                    value.find(' ') == -1,
                    value[-1] != ':'
                ]
            ), 'must be a CURIE'

        if isinstance(v, str):
            _is_curie(v)
        elif isinstance(v, list):
            for item in v:
                _is_curie(item)
    return v


class GenomicRegion(BaseModel):
    """Define GenomicRegion class"""

    type = 'LocationDescription'
    description: Optional[str] = None
    value: Union[SequenceLocation, ChromosomeLocation]


class TranscriptComponent(BaseModel):
    """Define TranscriptComponent class"""

    component_type = 'transcript_segment'
    transcript: str
    exon_start: StrictInt
    exon_start_offset: StrictInt = 0
    exon_end: StrictInt
    exon_end_offset: StrictInt = 0
    gene: GeneDescriptor
    component_genomic_region: GenomicRegion

    _validate_transcript = \
        validator('transcript', allow_reuse=True)(check_curie)


class CriticalDomain(BaseModel):
    """Define CriticalDomain class"""

    status: StrictStr
    name: str
    id: str
    gene: GeneDescriptor

    _validate_id = validator('id', allow_reuse=True)(check_curie)

    @validator('status')
    def correct_status(cls, v):
        """Validate status"""
        assert v.lower() == 'lost' or v == 'preserved', 'status must ' \
                                                        'be either lost ' \
                                                        'or preserved'
        return v


class Event(BaseModel):
    """Define Event class (causative event)"""

    event_type: str

    @validator('event_type')
    def event_validate(cls, v):
        """Validate event_type"""
        assert v.lower() == 'rearrangement' or v == 'read-through' or \
               v == 'trans-splicing', 'event entry must be one of ' \
                                      'rearrangement, read-through, ' \
                                      'or trans-splicing'
        return v


class Linker(BaseModel):
    """Define Linker class (linker sequence)"""

    linker_sequence: str
    component_type = 'linker_sequence'

    @validator('linker_sequence')
    def valid_input(cls, v):
        """Validate linker_sequence"""
        assert set(v.upper()) <= set('ACGT'), 'Linker sequence must ' \
                                              'only contain A,C,G,T'
        return v


class UnknownGene(BaseModel):
    """Define UnknownGene class"""

    component_type = 'unknown_gene'
    region: Optional[Union[SequenceLocation, ChromosomeLocation]]


class RegulatoryElement(BaseModel):
    """Define RegulatoryElement class"""

    type: str
    value_id: str
    label: StrictStr

    _validate_value_id = validator('value_id', allow_reuse=True)(check_curie)

    @validator('type')
    def valid_reg_type(cls, v):
        """Validate type"""
        assert v.lower() == 'promoter' or v == 'enhancer', 'type must be ' \
                                                           'either promoter ' \
                                                           'or enhancer'
        return v


class Fusion(BaseModel):
    """Define Fusion class"""

    r_frame_preserved: StrictBool
    regulatory_elements: List[RegulatoryElement]
    protein_domains: List[CriticalDomain]
    transcript_components: List[Union[TranscriptComponent, Linker,
                                      UnknownGene]]
    causative_event: Event

    def make_json(self):
        """JSON helper function"""
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
