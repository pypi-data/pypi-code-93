import logging

from .categorical_summary_generator import CategoricalSummaryGenerator
from superwise.resources.superwise_enums import BooleanSecondaryType


logger = logging.getLogger(__name__)


class BooleanSummaryGenerator(CategoricalSummaryGenerator):
    def generate_summary(self, secondary_type: str):
        secondary_type_to_metrics = {
            BooleanSecondaryType.FLAG.value: [self.calc_missing_values, self.calc_new_values, self.calc_distribution],
            BooleanSecondaryType.NUMERIC.value: [
                self.calc_missing_values,
                self.calc_new_values,
                self.calc_distribution,
            ],
        }
        logger.debug(f"Generate summary for boolean ({secondary_type}) feature {self._entity.name}")
        summary = {}
        for metric in secondary_type_to_metrics[secondary_type]:
            summary = self._update(summary, metric())
        return summary
