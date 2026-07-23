"""Quantum Security Toolkit (QST) package initialization.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/07_SYSTEM_ARCHITECTURE.md
"""

from qst.config.settings import QST_VERSION
from qst.exceptions.base import QSTError
from qst.exceptions.validation import ValidationError
from qst.models.config import SimulationConfig, SecurityThresholds, ProtocolType
from qst.models.results import (
    SimulationResult,
    ExperimentMetadata,
    ExecutionMetrics,
    ExperimentResult,
    SweepDimensions,
    ParameterSweepResult,
    StatisticsResult,
)
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.orchestration.statistics import ExperimentStatisticsService
from qst.orchestration.sweep_generator import ParameterSweepGenerator

__version__ = QST_VERSION

__all__ = [
    "SimulationOrchestrator",
    "SimulationResult",
    "QSTError",
    "ValidationError",
    "SimulationConfig",
    "SecurityThresholds",
    "ProtocolType",
    "ExperimentMetadata",
    "ExecutionMetrics",
    "ExperimentResult",
    "SweepDimensions",
    "ParameterSweepResult",
    "StatisticsResult",
    "ExperimentStatisticsService",
    "ParameterSweepGenerator",
]
