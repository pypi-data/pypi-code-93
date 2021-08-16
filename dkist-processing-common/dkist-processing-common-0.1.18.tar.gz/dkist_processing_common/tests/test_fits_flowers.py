import pytest
from astropy.io import fits

from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.parsers.cs_step import CSStepFlower
from dkist_processing_common.parsers.cs_step import NumCSStepBud
from dkist_processing_common.parsers.proposal_id_bud import ProposalIdBud
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import UniqueBud


class FitsReader(FitsAccessBase):
    def __init__(self, hdu, name):
        super().__init__(hdu, name)
        self.thing_id: int = self.header["id_key"]
        self.constant_thing: float = self.header["constant"]
        self.name = name
        self.proposal_id: str = self.header.get("ID___013")
        self.ip_task_type: str = self.header.get("DKIST004")


@pytest.fixture()
def basic_header_objs():
    header_dict = {
        "thing0": fits.header.Header(
            {"id_key": 0, "constant": 6.28, "DKIST004": "observe", "ID___013": "proposal_id_1"}
        ),
        "thing1": fits.header.Header(
            {"id_key": 1, "constant": 6.28, "DKIST004": "observe", "ID___013": "proposal_id_1"}
        ),
        "thing2": fits.header.Header(
            {"id_key": 2, "constant": 6.28, "DKIST004": "dark", "ID___013": "proposal_id_2"}
        ),
        "thing3": fits.header.Header(
            {"id_key": 0, "constant": 6.28, "DKIST004": "observe", "ID___013": "proposal_id_1"}
        ),
    }
    return (FitsReader.from_header(header, name=path) for path, header in header_dict.items())


@pytest.fixture()
def bad_header_objs():
    bad_headers = {
        "thing0": fits.header.Header({"id_key": 0, "constant": 6.28}),
        "thing1": fits.header.Header({"id_key": 1, "constant": 3.14}),
    }
    return (FitsReader.from_header(header, name=path) for path, header in bad_headers.items())


def test_unique_bud(basic_header_objs):
    """
    Given: A set of headers with a constant value header key
    When: Ingesting headers with a UniqueRock and asking for the value
    Then: The Rock's value is the header constant value
    """
    bud = UniqueBud(
        constant_name="constant",
        metadata_key="constant_thing",
    )
    assert bud.stem_name == "constant"
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == 6.28


def test_unique_bud_non_unique_inputs(bad_header_objs):
    """
    Given: A set of headers with a non-constant header key that is expected to be constant
    When: Ingesting headers with a UniqueRock and asking for the value
    Then: An error is raised
    """
    rock = UniqueBud(
        constant_name="constant",
        metadata_key="constant_thing",
    )
    assert rock.stem_name == "constant"
    for fo in bad_header_objs:
        key = fo.name
        rock.update(key, fo)

    with pytest.raises(ValueError):
        assert next(rock.petals)


def test_single_value_single_key_flower(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with a single key that has a limited set of values
    When: Ingesting with a SingleValueSingleKeyFlower and asking for the grouping
    Then: The filepaths are grouped correctly based on the header key value
    """
    flower = SingleValueSingleKeyFlower(tag_stem_name="id", metadata_key="thing_id")
    assert flower.stem_name == "id"
    for fo in basic_header_objs:
        key = fo.name
        flower.update(key, fo)

    petals = sorted(list(flower.petals), key=lambda x: x.value)
    assert len(petals) == 3
    assert petals[0].value == 0
    assert petals[0].keys == ["thing0", "thing3"]
    assert petals[1].value == 1
    assert petals[1].keys == ["thing1"]
    assert petals[2].value == 2
    assert petals[2].keys == ["thing2"]


def test_cs_step_flower(grouped_cal_sequence_headers, non_polcal_headers):
    """
    Given: A set of PolCal headers, non-PolCal headers, and the CSStepFlower
    When: Updating the CSStepFlower with all headers
    Then: The flower correctly organizes the PolCal frames and ignores the non-PolCal frames
    """
    cs_step_flower = CSStepFlower()
    for step, headers in grouped_cal_sequence_headers.items():
        for i, h in enumerate(headers):
            key = f"step_{step}_file_{i}"
            cs_step_flower.update(key, h)

    for h in non_polcal_headers:
        cs_step_flower.update("non_polcal", h)

    assert len(list(cs_step_flower.petals)) == len(list(grouped_cal_sequence_headers.keys()))
    for step_petal in cs_step_flower.petals:
        assert sorted(step_petal.keys) == [
            f"step_{step_petal.value}_file_{i}" for i in range(len(step_petal.keys))
        ]


def test_num_cs_step_bud(grouped_cal_sequence_headers, non_polcal_headers):
    """
    Given: A set of PolCal headers, non-PolCal headers, and the NumCSStepRock
    When: Updating the NumCSStepRock with all headers
    Then: The rock reports the correct number of CS Steps (thus ignoring the non-PolCal frames)
    """
    num_cs_bud = NumCSStepBud()
    for step, headers in grouped_cal_sequence_headers.items():
        for h in headers:
            num_cs_bud.update(step, h)

    for h in non_polcal_headers:
        num_cs_bud.update("foo", h)

    bud = list(num_cs_bud.petals)
    assert len(bud) == 1
    assert bud[0].value == len(grouped_cal_sequence_headers.keys())


def test_proposal_id_bud(basic_header_objs):
    bud = ProposalIdBud()
    assert bud.stem_name == "PROPOSAL_ID"
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == "proposal_id_1"
