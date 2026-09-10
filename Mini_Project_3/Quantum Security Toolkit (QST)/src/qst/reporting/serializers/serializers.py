"""Serializer abstract interface and concrete domain model serializers.

References:
    Docs/10_API_SPECIFICATION.md §5
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

import abc
from enum import Enum
from typing import Any, Optional

from qst.models.results import (
    EveSimulationResult,
    ExperimentResult,
    ParameterSweepResult,
    QBERResult,
    ReconciliationResult,
    SecurityMetrics,
    SiftedKeyResult,
    SimulationResult,
)


class ExportFormat(Enum):
    """Enumeration of supported serialization export formats."""

    JSON = "JSON"
    CSV = "CSV"


class Serializer(abc.ABC):
    """Abstract base class for QST domain model serializers."""

    @abc.abstractmethod
    def serialize(self, data: Any) -> dict[str, Any]:
        """Convert a domain model into a normalized dictionary structure.

        Args:
            data: The domain model instance to serialize.

        Returns:
            A dictionary containing primitive representation of the model.
        """
        pass


class SimulationSerializer(Serializer):
    """Converts a SimulationResult into a nested dictionary structure."""

    def serialize(self, data: Any) -> dict[str, Any]:
        """Normalize a SimulationResult object.

        Args:
            data: A SimulationResult instance.

        Returns:
            A normalized dictionary representation.
        """
        if not isinstance(data, SimulationResult):
            raise TypeError(
                "SimulationSerializer only supports SimulationResult objects."
            )

        # Serialize nested value objects
        recon_dict = self._serialize_reconciliation(data.reconciliation)
        sifted_dict = self._serialize_sifted_keys(data.sifted_keys)
        eve_dict = self._serialize_eve_simulation(data.eve_simulation)
        qber_dict = self._serialize_qber_result(data.qber_result)
        metrics_dict = self._serialize_security_metrics(data.security_metrics)

        return {
            "qber": data.qber,
            "final_key_length": data.final_key_length,
            "key_rate": data.key_rate,
            "sifted_key": data.sifted_key,
            "n_qubits": data.n_qubits,
            "seed": data.seed,
            "eve_intercept_probability": data.eve_intercept_probability,
            "interception_probability": data.interception_probability,
            "warnings": data.warnings,
            "metadata": data.metadata,
            "alice_bits": data.alice_bits,
            "bob_bits": data.bob_bits,
            "alice_bases": data.alice_bases,
            "bob_bases": data.bob_bases,
            "reconciliation": recon_dict,
            "sifted_keys": sifted_dict,
            "eve_simulation": eve_dict,
            "qber_result": qber_dict,
            "security_metrics": metrics_dict,
        }

    def _serialize_reconciliation(
        self, recon: Optional[ReconciliationResult]
    ) -> Optional[dict[str, Any]]:
        if recon is None:
            return None
        return {
            "matching_indices": recon.matching_indices,
            "discarded_indices": recon.discarded_indices,
            "matching_bases": recon.matching_bases,
            "total_bits": recon.total_bits,
            "matching_count": recon.matching_count,
            "match_rate": recon.match_rate,
        }

    def _serialize_sifted_keys(
        self, sifted: Optional[SiftedKeyResult]
    ) -> Optional[dict[str, Any]]:
        if sifted is None:
            return None
        return {
            "alice_key": sifted.alice_key,
            "bob_key": sifted.bob_key,
            "key_length": sifted.key_length,
        }

    def _serialize_eve_simulation(
        self, eve: Optional[EveSimulationResult]
    ) -> Optional[dict[str, Any]]:
        if eve is None:
            return None
        return {
            "intercepted_mask": eve.intercepted_mask,
            "eve_bases": eve.eve_bases,
            "eve_measurements": eve.eve_measurements,
            "reconstructed_bits": eve.reconstructed_bits,
            "reconstructed_bases": eve.reconstructed_bases,
        }

    def _serialize_qber_result(
        self, qb: Optional[QBERResult]
    ) -> Optional[dict[str, Any]]:
        if qb is None:
            return None
        return {
            "error_count": qb.error_count,
            "sifted_key_length": qb.sifted_key_length,
            "qber": qb.qber,
            "confidence_notes": qb.confidence_notes,
        }

    def _serialize_security_metrics(
        self, sm: Optional[SecurityMetrics]
    ) -> Optional[dict[str, Any]]:
        if sm is None:
            return None
        return {
            "key_rate": sm.key_rate,
            "discard_rate": sm.discard_rate,
            "error_rate": sm.error_rate,
            "status": sm.status.value,
        }


class ExperimentSerializer(Serializer):
    """Converts an ExperimentResult into a nested dictionary structure."""

    def serialize(self, data: Any) -> dict[str, Any]:
        """Normalize an ExperimentResult object.

        Args:
            data: An ExperimentResult instance.

        Returns:
            A normalized dictionary representation.
        """
        if not isinstance(data, ExperimentResult):
            raise TypeError(
                "ExperimentSerializer only supports ExperimentResult objects."
            )

        sim_serializer = SimulationSerializer()
        serialized_simulations = [
            sim_serializer.serialize(sim) for sim in data.simulations
        ]

        return {
            "simulations": serialized_simulations,
            "average_qber": data.average_qber,
            "average_key_rate": data.average_key_rate,
            "secure_runs": data.secure_runs,
            "warning_runs": data.warning_runs,
            "compromised_runs": data.compromised_runs,
            "metrics": {
                "execution_time": data.metrics.execution_time,
                "average_simulation_time": data.metrics.average_simulation_time,
                "throughput": data.metrics.throughput,
                "simulations_per_second": data.metrics.simulations_per_second,
            },
            "metadata": {
                "protocol": data.metadata.protocol,
                "timestamp": data.metadata.timestamp,
                "qiskit_version": data.metadata.qiskit_version,
                "repetitions": data.metadata.repetitions,
                "seed_strategy": data.metadata.seed_strategy,
            },
        }


class ParameterSweepSerializer(Serializer):
    """Converts a ParameterSweepResult into a nested dictionary structure."""

    def serialize(self, data: Any) -> dict[str, Any]:
        """Normalize a ParameterSweepResult object.

        Args:
            data: A ParameterSweepResult instance.

        Returns:
            A normalized dictionary representation.
        """
        if not isinstance(data, ParameterSweepResult):
            raise TypeError(
                "ParameterSweepSerializer only supports ParameterSweepResult objects."
            )

        exp_serializer = ExperimentSerializer()
        serialized_experiments = [
            exp_serializer.serialize(exp) for exp in data.experiments
        ]

        return {
            "experiments": serialized_experiments,
            "total_experiments": data.total_experiments,
            "sweep_dimensions": {
                "qubit_counts": data.sweep_dimensions.qubit_counts,
                "interception_probabilities": data.sweep_dimensions.interception_probabilities,
                "seeds": data.sweep_dimensions.seeds,
            },
            "metadata": {
                "protocol": data.metadata.protocol,
                "timestamp": data.metadata.timestamp,
                "qiskit_version": data.metadata.qiskit_version,
                "repetitions": data.metadata.repetitions,
                "seed_strategy": data.metadata.seed_strategy,
            },
        }
