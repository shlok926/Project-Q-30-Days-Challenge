"""Simulation Orchestrator implementation for coordinates sweeps and executions.

References:
    Docs/SIMULATION_SPEC.md §1-§6
    Docs/07_SYSTEM_ARCHITECTURE.md §5, §11
"""

import datetime
import inspect
import time
from typing import Callable, Optional, Sequence

import numpy as np
import qiskit

from qst.interfaces.protocol import ProtocolInterface
from qst.models.config import ProtocolType, SimulationConfig
from qst.models.results import (
    ExecutionMetrics,
    ExperimentMetadata,
    ExperimentResult,
    ParameterSweepResult,
    SecurityStatus,
    SimulationResult,
    SweepDimensions,
)


class SimulationOrchestrator:
    """Coordinates execution of QKD protocol simulations over interfaces."""

    def __init__(
        self,
        protocol_factory: Optional[Callable[[ProtocolType], ProtocolInterface]] = None,
    ) -> None:
        """Initialize the SimulationOrchestrator.

        Args:
            protocol_factory: Optional factory function mapping ProtocolType to ProtocolInterface.
        """
        if protocol_factory is None:
            from qst.core.bb84.protocol import BB84Protocol

            self._protocol_factory = lambda p_type: BB84Protocol()
        else:
            self._protocol_factory = protocol_factory

    def run_once(self, config: SimulationConfig) -> ExperimentResult:
        """Execute a single simulation trial for the given configuration.

        Args:
            config: Parameter configurations defining the run.

        Returns:
            An ExperimentResult containing outcomes.
        """
        single_config = SimulationConfig(
            n_qubits=config.n_qubits,
            seed=config.seed,
            interception_probability=config.interception_probability,
            repetitions=1,
            security_thresholds=config.security_thresholds,
            protocol=config.protocol,
        )
        return self.run_many(single_config)

    def run_many(self, config: SimulationConfig) -> ExperimentResult:
        """Execute repeated simulation trials for the given configuration.

        Args:
            config: Parameter configurations defining the run repetitions.

        Returns:
            An ExperimentResult aggregating outcomes of all repetitions.
        """
        repetitions = config.repetitions
        n_qubits = config.n_qubits

        # Generate seed sub-sequence to preserve determinism
        if config.seed is not None:
            rng = np.random.default_rng(config.seed)
            seeds = rng.integers(0, 1000000, size=repetitions)
        else:
            seeds = [None] * repetitions

        simulations: list[SimulationResult] = []
        simulation_times: list[float] = []

        t_start_batch = time.perf_counter()

        for j in range(repetitions):
            protocol = self._protocol_factory(config.protocol)

            t_start_run = time.perf_counter()

            # Dynamically inspect parameter requirements of initialize
            sig = inspect.signature(protocol.initialize)
            init_kwargs = {
                "n_qubits": n_qubits,
                "seed": int(seeds[j]) if seeds[j] is not None else None,
            }
            if "eve_intercept_probability" in sig.parameters:
                init_kwargs["eve_intercept_probability"] = (
                    config.interception_probability
                )

            protocol.initialize(**init_kwargs)
            protocol.execute()
            protocol.measure()

            res = protocol.export()
            simulations.append(res)

            simulation_times.append(time.perf_counter() - t_start_run)

        t_elapsed_batch = time.perf_counter() - t_start_batch

        # Aggregate outcomes
        secure_count = 0
        warning_count = 0
        compromised_count = 0
        qbers = []
        key_rates = []

        for sim in simulations:
            if sim.security_metrics:
                status = sim.security_metrics.status
                if status == SecurityStatus.SECURE:
                    secure_count += 1
                elif status == SecurityStatus.WARNING:
                    warning_count += 1
                elif status == SecurityStatus.COMPROMISED:
                    compromised_count += 1

            if sim.qber is not None:
                qbers.append(sim.qber)
            if sim.key_rate is not None:
                key_rates.append(sim.key_rate)

        avg_qber = float(np.mean(qbers)) if qbers else 0.0
        avg_key_rate = float(np.mean(key_rates)) if key_rates else 0.0

        # Calculate metrics
        avg_sim_time = float(np.mean(simulation_times)) if simulation_times else 0.0
        total_qubits = n_qubits * repetitions
        throughput = (
            float(total_qubits / t_elapsed_batch) if t_elapsed_batch > 0 else 0.0
        )
        sims_per_sec = (
            float(repetitions / t_elapsed_batch) if t_elapsed_batch > 0 else 0.0
        )

        metrics = ExecutionMetrics(
            execution_time=t_elapsed_batch,
            average_simulation_time=avg_sim_time,
            throughput=throughput,
            simulations_per_second=sims_per_sec,
        )

        metadata = ExperimentMetadata(
            protocol=config.protocol.value,
            timestamp=datetime.datetime.now().isoformat(),
            qiskit_version=qiskit.__version__,
            repetitions=repetitions,
            seed_strategy=(
                "seeded-sub-generators"
                if config.seed is not None
                else "non-deterministic"
            ),
        )

        return ExperimentResult(
            simulations=tuple(simulations),
            average_qber=avg_qber,
            average_key_rate=avg_key_rate,
            secure_runs=secure_count,
            warning_runs=warning_count,
            compromised_runs=compromised_count,
            metrics=metrics,
            metadata=metadata,
        )

    def run_parameter_sweep(
        self,
        configs: Sequence[SimulationConfig],
        sweep_dimensions: SweepDimensions,
    ) -> ParameterSweepResult:
        """Execute configurations defined in a parameter sweep grid.

        Args:
            configs: Sequence of SimulationConfig configuration coordinates.
            sweep_dimensions: Dimensional parameters checked.

        Returns:
            A ParameterSweepResult aggregating results.
        """
        experiments: list[ExperimentResult] = []

        t_start_sweep = time.perf_counter()

        for config in configs:
            experiments.append(self.run_many(config))

        t_elapsed_sweep = time.perf_counter() - t_start_sweep

        # Construct global metadata using the first configuration as reference
        ref_config = configs[0] if configs else SimulationConfig(n_qubits=10)

        global_metadata = ExperimentMetadata(
            protocol=ref_config.protocol.value,
            timestamp=datetime.datetime.now().isoformat(),
            qiskit_version=qiskit.__version__,
            repetitions=ref_config.repetitions,
            seed_strategy=(
                "seeded-sub-generators"
                if ref_config.seed is not None
                else "non-deterministic"
            ),
        )

        return ParameterSweepResult(
            experiments=tuple(experiments),
            total_experiments=len(experiments),
            sweep_dimensions=sweep_dimensions,
            metadata=global_metadata,
        )
