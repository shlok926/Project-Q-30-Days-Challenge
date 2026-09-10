"""Standard configuration fixtures for the QST test suite.

References:
    Docs/14_TESTING_STRATEGY.md
"""

from typing import Any

import pytest

from qst.config.settings import Configuration


@pytest.fixture(scope="session")
def qst_config() -> Configuration:
    """Session-scoped configuration instance.

    Returns:
        The running Configuration instance.
    """
    return Configuration()


@pytest.fixture
def mock_simulation_data() -> dict[str, Any]:
    """A dictionary providing standard inputs for simulation validation.

    Returns:
        Sample valid inputs.
    """
    return {
        "n_qubits": 100,
        "seed": 42,
        "eve_intercept_probability": 0.5,
    }
