# pysimdata

Python simulation data processing project.

## Requirements

- Python ≥ 3.9
- `venv` (built into Python 3.3+)
- Optional but recommended: VSCode + the recommended extensions for the best experience.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
```

This installs the package in editable mode along with dev dependencies (pytest, pytest-cov, ruff).

## Run

```bash
python -m pysimdata
# or
python -c "import pysimdata; print(pysimdata.__version__)"
```

## Test

```bash
pytest
```

Test files go under `tests/<module_name>/test_<...>.py` — pytest auto-discovers them via the `testpaths` setting in `pyproject.toml`.

## Lint / format

```bash
ruff check .        # lint
ruff format .      # format
```

## Debug

Open the folder in VSCode (`code .`). The project ships launch configurations (`.vscode/launch.json`):

- **Python: Current File** — debug the file currently open in the editor.
- **Python: Module pysimdata** — debug the package as a module (entry point).
- **Python: pytest** — debug all tests.
- **Python: pytest current file** — debug the test file currently open.

`settings.json` points VSCode at `.venv/bin/python`, so IntelliSense, breakpoints, and the test explorer all use the correct interpreter. Ruff is set as the default formatter, with format-on-save enabled.

If you don't use VSCode, attach from the command line:

```bash
python -m pdb -m pysimdata
# or
pytest --pdb                  # drops into pdb on first failure
```

## Project layout

- `docs/` — design docs and plans (use `docs/plan-template.md`)
- `src/pysimdata/` — package source
- `tests/` — pytest tests, organized by module

## Conventions

See `CLAUDE.md` at the project root.