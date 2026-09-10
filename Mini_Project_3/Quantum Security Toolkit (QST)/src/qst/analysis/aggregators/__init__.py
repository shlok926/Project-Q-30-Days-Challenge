"""Exports for aggregators package.

References:
    Docs/10_API_SPECIFICATION.md §5
"""

from qst.analysis.aggregators.aggregator import (
    AggregationResult,
    ExperimentAggregator,
)

__all__ = ["ExperimentAggregator", "AggregationResult"]
