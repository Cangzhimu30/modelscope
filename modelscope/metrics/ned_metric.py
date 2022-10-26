# Copyright (c) Alibaba, Inc. and its affiliates.

from typing import Dict

import numpy as np
from similarity.normalized_levenshtein import NormalizedLevenshtein

from modelscope.metainfo import Metrics
from modelscope.outputs import OutputKeys
from modelscope.utils.registry import default_group
from .base import Metric
from .builder import METRICS, MetricKeys


@METRICS.register_module(group_key=default_group, module_name=Metrics.NED)
class NedMetric(Metric):
    """The metric computation class for classification classes.

    This metric class calculates accuracy for the whole input batches.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ned = NormalizedLevenshtein()
        self.preds = []
        self.labels = []

    def add(self, outputs: Dict, inputs: Dict):
        label_name = OutputKeys.LABEL if OutputKeys.LABEL in inputs else OutputKeys.LABELS
        ground_truths = inputs[label_name]
        eval_results = outputs[label_name]
        for key in [
                OutputKeys.CAPTION, OutputKeys.TEXT, OutputKeys.BOXES,
                OutputKeys.LABELS, OutputKeys.SCORES
        ]:
            if key in outputs and outputs[key] is not None:
                eval_results = outputs[key]
                break
        assert type(ground_truths) == type(eval_results)
        if isinstance(ground_truths, list):
            self.preds.extend(eval_results)
            self.labels.extend(ground_truths)
        elif isinstance(ground_truths, np.ndarray):
            self.preds.extend(eval_results.tolist())
            self.labels.extend(ground_truths.tolist())
        else:
            raise 'only support list or np.ndarray'

    def evaluate(self):
        assert len(self.preds) == len(self.labels)
        return {
            MetricKeys.NED: (np.asarray([
                self.ned.distance(pred, ref)
                for pred, ref in zip(self.preds, self.labels)
            ])).mean().item()
        }
