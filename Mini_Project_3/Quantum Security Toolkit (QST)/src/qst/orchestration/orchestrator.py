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

            self._protocol_factory = lambda p_type, exec_val=None: BB84Protocol(
                executor=exec_val
            )
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
            use_ibm_runtime=config.use_ibm_runtime,
            backend_name=config.backend_name,
            ibm_token=config.ibm_token,
            noise_aware_local=config.noise_aware_local,
            fallback_to_aer=config.fallback_to_aer,
            run_error_correction=config.run_error_correction,
            cascade_configuration=config.cascade_configuration,
            run_privacy_amplification=config.run_privacy_amplification,
            privacy_configuration=config.privacy_configuration,
            security_classification_thresholds=config.security_classification_thresholds,
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

        # Initialize executor based on config
        executor = None
        if getattr(config, "use_ibm_runtime", False):
            try:
                from qst.core.shared.execution.ibm_runtime_executor import (
                    IBMRuntimeExecutor,
                )

                executor = IBMRuntimeExecutor(
                    backend_name=getattr(config, "backend_name", None),
                    token=getattr(config, "ibm_token", None),
                    noise_aware_local=getattr(config, "noise_aware_local", False),
                )
            except Exception as e:
                if getattr(config, "fallback_to_aer", True):
                    print(
                        f"[Warning] Fallback to AerExecutor triggered due to IBM Quantum Runtime error: {e}"
                    )
                    # executor remains None, falling back to AerExecutor
                else:
                    raise e

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
            # Instantiate protocol, supporting custom lambdas or legacy factories
            try:
                protocol = self._protocol_factory(config.protocol, exec_val=executor)
            except TypeError:
                protocol = self._protocol_factory(config.protocol)
                if executor is not None and hasattr(protocol, "_executor"):
                    object.__setattr__(protocol, "_executor", executor)

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

            fell_back = False
            try:
                protocol.execute()
                protocol.measure()
            except Exception as e:
                # If execution fails and we are configured to fallback to Aer
                if getattr(config, "use_ibm_runtime", False) and getattr(
                    config, "fallback_to_aer", True
                ):
                    fell_back = True
                    print(
                        f"[Warning] Fallback to AerExecutor triggered during execution due to error: {e}"
                    )
                    from qst.core.shared.execution.executor import AerExecutor

                    fallback_exec = AerExecutor()
                    try:
                        protocol = self._protocol_factory(
                            config.protocol, exec_val=fallback_exec
                        )
                    except TypeError:
                        protocol = self._protocol_factory(config.protocol)
                        if hasattr(protocol, "_executor"):
                            object.__setattr__(protocol, "_executor", fallback_exec)
                    protocol.initialize(**init_kwargs)
                    protocol.execute()
                    protocol.measure()
                else:
                    raise e

            res = protocol.export()

            if getattr(config, "run_error_correction", False):
                from qst.correction.cascade import CascadeReconciler
                from qst.correction.models import CascadeConfiguration
                from dataclasses import replace

                cascade_config = getattr(config, "cascade_configuration", None)
                if cascade_config is None:
                    cascade_config = CascadeConfiguration()

                reconciler = CascadeReconciler(cascade_config)
                alice_sifted = res.sifted_keys.alice_key if res.sifted_keys else ()
                bob_sifted = res.sifted_keys.bob_key if res.sifted_keys else ()

                if alice_sifted and bob_sifted:
                    corr_result = reconciler.reconcile(alice_sifted, bob_sifted)
                    res = replace(
                        res,
                        corrected_key=list(corr_result.corrected_key.key_bits),
                        error_correction=corr_result,
                    )

            if getattr(config, "run_privacy_amplification", False):
                from qst.privacy.amplifier import PrivacyAmplifier
                from qst.privacy.models import PrivacyAmplificationConfiguration
                from dataclasses import replace

                privacy_config = getattr(config, "privacy_configuration", None)
                if privacy_config is None:
                    privacy_config = PrivacyAmplificationConfiguration()

                input_key = (
                    res.corrected_key
                    if res.corrected_key is not None
                    else res.sifted_key
                )

                if input_key:
                    amplifier = PrivacyAmplifier(privacy_config)
                    initial_qber = res.qber if res.qber is not None else 0.0
                    priv_result = amplifier.amplify(
                        input_key, initial_qber=initial_qber
                    )
                    res = replace(
                        res,
                        privacy_result=priv_result,
                        final_secret_key=priv_result.final_secret_key,
                        final_key_length=priv_result.output_key_length,
                        key_rate=(
                            float(priv_result.output_key_length / res.n_qubits)
                            if res.n_qubits > 0
                            else 0.0
                        ),
                    )

            if getattr(config, "use_ibm_runtime", False):
                if fell_back:
                    execution_mode = "Local Aer"
                elif getattr(config, "noise_aware_local", False):
                    execution_mode = "Noise-aware Aer"
                else:
                    execution_mode = "IBM Runtime"
            else:
                execution_mode = "Local Aer"

            from qst.secret.metrics import SecretMetricsCalculator
            from qst.secret.summary import ProtocolSummaryBuilder
            from qst.secret.models import SecurityClassificationConfig
            from dataclasses import replace

            classification_config = getattr(
                config, "security_classification_thresholds", None
            )
            metrics_calc = SecretMetricsCalculator(classification_config)
            summary_builder = ProtocolSummaryBuilder()

            raw_len = len(res.raw_key) if res.raw_key is not None else 0
            sifted_len = len(res.sifted_key) if res.sifted_key is not None else 0
            corrected_len = (
                len(res.corrected_key) if res.corrected_key is not None else None
            )

            if res.final_secret_key is not None:
                final_len = len(res.final_secret_key.key_bits)
            elif corrected_len is not None:
                final_len = corrected_len
            else:
                final_len = sifted_len

            sec_param = 0.0
            if res.privacy_result is not None:
                sec_param = res.privacy_result.statistics.estimated_security_parameter

            metrics = metrics_calc.calculate_metrics(
                raw_len=raw_len,
                sifted_len=sifted_len,
                corrected_len=corrected_len,
                final_len=final_len,
                security_parameter=sec_param,
            )

            sec_level = metrics_calc.classify_security_level(sec_param)

            summary = summary_builder.build_summary(
                raw_len=raw_len,
                sifted_len=sifted_len,
                corrected_len=corrected_len,
                final_len=final_len,
                qber=res.qber if res.qber is not None else 0.0,
                correction_enabled=getattr(config, "run_error_correction", False),
                privacy_enabled=getattr(config, "run_privacy_amplification", False),
                overall_success=True,
                execution_mode=execution_mode,
            )

            res = replace(
                res,
                protocol_summary=summary,
                secret_key_metrics=metrics,
                security_level=sec_level,
            )

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
