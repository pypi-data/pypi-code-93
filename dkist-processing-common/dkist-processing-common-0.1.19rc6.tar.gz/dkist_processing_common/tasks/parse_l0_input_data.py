"""
Common task to populate pipeline Constants and group files with tags by scanning headers
"""
import json
import logging
from pathlib import Path
from typing import List
from typing import Tuple
from typing import TypeVar

from astropy.io import fits
from astropy.io.fits import HDUList
from dkist_header_validator import spec122_validator

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import FlowerPot
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.cs_step import CSStepFlower
from dkist_processing_common.parsers.cs_step import NumCSStepBud
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.proposal_id_bud import ProposalIdBud
from dkist_processing_common.parsers.time import AverageCadenceBud
from dkist_processing_common.parsers.time import MaximumCadenceBud
from dkist_processing_common.parsers.time import MinimumCadenceBud
from dkist_processing_common.parsers.time import TimeOrderBud
from dkist_processing_common.parsers.time import VarianceCadenceBud
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.tasks.base import ScienceTaskL0ToL1Base
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin


__all__ = ["ParseL0InputData"]


logger = logging.getLogger(__name__)
S = TypeVar("S", bound=Stem)


class ParseL0InputData(ScienceTaskL0ToL1Base, InputDatasetMixin):
    @property
    def constant_flowers(self) -> List[S]:
        return [
            NumCSStepBud(self.input_dataset_parameters_get("MAX_CS_STEP_TIME_SEC")),
            UniqueBud(constant_name=BudName.instrument.value, metadata_key="instrument"),
            ProposalIdBud(),
            AverageCadenceBud(),
            MaximumCadenceBud(),
            MinimumCadenceBud(),
            VarianceCadenceBud(),
            TimeOrderBud(),
        ]

    @property
    def tag_flowers(self) -> List[S]:
        return [
            CSStepFlower(
                max_cs_step_time_sec=self.input_dataset_parameters_get("MAX_CS_STEP_TIME_SEC")
            ),
        ]

    @property
    def fits_parsing_class(self):
        return L0FitsAccess

    def run(self) -> None:

        with self.apm_step("Check that input frames exist"):
            self.check_input_frames()

        with self.apm_step("Ingest all input files"):
            tag_pot, constant_pot = self.make_flower_pots()

        with self.apm_step("Update constants"):
            self.update_constants(constant_pot)

        with self.apm_step("Tag files"):
            self.tag_petals(tag_pot)

    def make_flower_pots(self) -> Tuple[FlowerPot, FlowerPot]:
        """ Ingest all headers """
        tag_pot = FlowerPot()
        constant_pot = FlowerPot()
        tag_pot.flowers += self.tag_flowers
        constant_pot.flowers += self.constant_flowers

        for fits_obj in self.input_frames:
            filepath = fits_obj.name
            tag_pot.add_dirt(filepath, fits_obj)
            constant_pot.add_dirt(filepath, fits_obj)

        return tag_pot, constant_pot

    @property
    def input_frames(self):
        return list(
            self.fits_data_read_fits_access(
                tags=[Tag.input(), Tag.frame()], cls=self.fits_parsing_class
            )
        )

    def check_input_frames(self):
        """
        Helper function to make sure that at least one tagged frame exists before doing anything else
        """
        if len(self.input_frames) == 0:
            raise ValueError("No frames were tagged with INPUT and FRAME")

    def update_constants(self, constant_pot: FlowerPot):
        """ Update pipeline Constants """
        for flower in constant_pot:
            try:
                # If the value is a set, sort it before storing in redis
                if isinstance(flower.bud.value, set):
                    sorted_value = json.dumps(sorted(flower.bud.value))
                    self.constants.update({flower.stem_name: sorted_value})
                else:
                    self.constants.update({flower.stem_name: flower.bud.value})
            except StopIteration:
                # There are no petals
                pass

    def tag_petals(self, tag_pot: FlowerPot):
        """ Apply tags to file paths """
        for flower in tag_pot:
            for petal in flower.petals:
                tag = Tag.format_tag(flower.stem_name, petal.value)
                for path in petal.keys:
                    self.tag(path, tag)
