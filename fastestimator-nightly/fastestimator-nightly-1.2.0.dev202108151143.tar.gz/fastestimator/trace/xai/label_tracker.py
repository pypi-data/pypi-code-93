#  Copyright 2021 The FastEstimator Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ==============================================================================
import statistics as stats
from collections import defaultdict
from typing import Any, Dict, Iterable, Optional, Set, Union

from fastestimator.summary.summary import Summary, ValWithError
from fastestimator.trace.trace import Trace
from fastestimator.util.data import Data
from fastestimator.util.traceability_util import traceable
from fastestimator.util.util import DefaultKeyDict, to_number, to_set


@traceable()
class LabelTracker(Trace):
    """A Trace to track metrics grouped by labels, for example per-class loss over time during training.

    Use this in conjunction with ImageViewer or ImageSaver to see the graph at training end. This also automatically
    integrates with Traceability reports.

    Args:
        label: The key of the labels by which to group data.
        metric: The key of the metric by which to score data.
        label_mapping: A mapping of {DisplayName: LabelValue} to use when generating the graph. This can also be used to
            limit which label values are graphed, since any label values not included here will not be graphed. A None
            value will monitor all label values.
        bounds: What error bounds should be graphed around the mean value. Options include None, 'std' for standard
            deviation, and 'range' to plot (min_value, mean, max_value). Multiple values can be specified, ex.
             ['std', 'range'] to generate multiple graphs.
        mode: What mode(s) to execute this Trace in. For example, "train", "eval", "test", or "infer". To execute
            regardless of mode, pass None. To execute in all modes except for a particular one, you can pass an argument
            like "!infer" or "!train".
        outputs: The name of the output which will be generated by this trace at the end of training. If None then it
            will default to "<metric>_by_<label>".

    Raises:
        ValueError: If `bounds` is not one of the allowed options.
    """
    def __init__(self,
                 label: str,
                 metric: str,
                 label_mapping: Optional[Dict[str, Any]] = None,
                 bounds: Union[None, str, Iterable[Union[str, None]]] = "std",
                 mode: Union[None, str, Set[str]] = "eval",
                 outputs: Optional[str] = None):
        super().__init__(inputs=[label, metric], outputs=outputs or f"{metric}_by_{label}", mode=mode)
        self.points = []
        self.label_summaries = DefaultKeyDict(default=lambda x: Summary(name=x))
        self.label_mapping = {val: key for key, val in label_mapping.items()} if label_mapping else None
        bounds = to_set(bounds)
        if not bounds:
            bounds.add(None)
        for option in bounds:
            if option not in (None, "std", "range"):
                raise ValueError(f"'interval' must be either None, 'std', or 'range', but got '{bounds}'.")
        self.bounds = bounds

    @property
    def label_key(self) -> str:
        return self.inputs[0]

    @property
    def metric_key(self) -> str:
        return self.inputs[1]

    def on_batch_end(self, data: Data) -> None:
        self.points.append((to_number(data[self.label_key]), to_number(data[self.metric_key])))

    def on_epoch_end(self, data: Data) -> None:
        label_scores = defaultdict(list)
        for batch in self.points:
            for label, metric in ((batch[0][i], batch[1][i]) for i in range(len(batch[0]))):
                label_scores[label.item()].append(metric.item())
        for label, metric in label_scores.items():
            if self.label_mapping:
                if label in self.label_mapping:
                    label = self.label_mapping[label]
                else:
                    # Skip labels which the user does not want to inspect
                    continue
            if 'std' in self.bounds:
                mean, std = stats.mean(metric), stats.stdev(metric) if len(metric) > 1 else 0.0
                val = ValWithError(mean - std, mean, mean + std)
                key = f"{self.metric_key} ($\\mu \\pm \\sigma$)"
                # {label: {mode: {key: {step: value}}}}
                self.label_summaries[label].history[self.system.mode][key][self.system.global_step] = val
            if 'range' in self.bounds:
                val = ValWithError(min(metric), stats.mean(metric), max(metric))
                key = f"{self.metric_key} ($min, \\mu, max$)"
                self.label_summaries[label].history[self.system.mode][key][self.system.global_step] = val
            if None in self.bounds:
                val = stats.mean(metric)
                key = self.metric_key
                self.label_summaries[label].history[self.system.mode][key][self.system.global_step] = val
        self.points = []

    def on_end(self, data: Data) -> None:
        self.system.add_graph(self.outputs[0], list(self.label_summaries.values()))  # So traceability can draw it
        data.write_without_log(self.outputs[0], list(self.label_summaries.values()))

    def __getstate__(self) -> Dict[str, Any]:
        """Get a representation of the state of this object.

        This method is invoked by pickle.

        Returns:
            The information to be recorded by a pickle summary of this object.
        """
        state = self.__dict__.copy()
        state['label_summaries'] = dict(state['label_summaries'])
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Set this objects internal state from a dictionary of variables.

        This method is invoked by pickle.

        Args:
            state: The saved state to be used by this object.
        """
        label_summaries = DefaultKeyDict(default=lambda x: Summary(name=x))
        label_summaries.update(state.get('label_summaries', {}))
        state['label_summaries'] = label_summaries
        self.__dict__.update(state)
