"""Analysis package exposing aggregators, comparisons, and trends services.

References:
    Docs/10_API_SPECIFICATION.md §5
"""

from qst.analysis.aggregators.aggregator import (
    AggregationResult,
    ExperimentAggregator,
)
from qst.analysis.comparisons.comparison import (
    ComparisonResult,
    ComparisonService,
)
from qst.analysis.trends.trends import TrendAnalysisService

__all__ = [
    "ExperimentAggregator",
    "AggregationResult",
    "TrendAnalysisService",
    "ComparisonService",
    "ComparisonResult",
]
