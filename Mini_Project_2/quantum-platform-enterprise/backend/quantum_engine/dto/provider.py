from pydantic import BaseModel

class ProviderCapabilities(BaseModel):
    supports_runtime: bool
    supports_sampler: bool
    supports_estimator: bool
    supports_dynamic_circuits: bool
    supports_pulse: bool
    supports_noise: bool
    supports_real_hardware: bool
    supports_simulator: bool
