@echo off
REM Prepare Python virtual environment and install dependencies using pyproject.toml

REM Check if .venv exists, create if not
if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
REM Install build backend if needed for PEP 517/518
python -m pip install build
REM Install all dependencies including dev extras from pyproject.toml
python -m pip install .[dev]

echo Environment setup complete. To activate later, run:
echo   call .venv\Scripts\activate.bat
