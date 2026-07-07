from interfaces.provider import QuantumProvider
from exceptions.quantum_exceptions import ProviderUnavailable
from providers.aer_provider import AerProvider
from providers.ibm_provider import IBMProvider

class QuantumProviderFactory:
    @staticmethod
    def get_provider(provider_type: str, credentials: dict = None) -> QuantumProvider:
        if provider_type == "aer":
            return AerProvider()
        elif provider_type == "ibm":
            if not credentials or "api_token" not in credentials:
                raise ProviderUnavailable("IBM Provider requires an 'api_token' in credentials.")
            return IBMProvider(api_token=credentials["api_token"])
        else:
            raise ProviderUnavailable(f"Provider {provider_type} is not implemented.")
