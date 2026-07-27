# Contributing to QST

Thank you for your interest in contributing to the Quantum Security Toolkit (QST)!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/shlok926/Project-Q-30-Days-Challenge.git
   cd "Mini_Project_3/Quantum Security Toolkit (QST)"
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt -r requirements.txt
   pip install -e .
   ```

## Development Guidelines

- **Code Style:** We use `black` for formatting and `ruff` for linting. Run:
  ```bash
  black src/ tests/ examples/
  ruff check src/ tests/ examples/
  ```
- **Static Typing:** Run `mypy` to verify types compatibility:
  ```bash
  mypy src/
  ```
- **Testing:** Add unit or integration tests for any new features. All tests must pass before submission:
  ```bash
  python -m pytest
  ```

## Pull Request Process

1. Create a branch from `main` using descriptive naming conventions.
2. Verify all linting, formatting, typing, and testing checks pass locally.
3. Open a pull request targeting `main`. Reference any associated issues.
4. Ensure your PR receives approval from at least one core maintainer before merging.
