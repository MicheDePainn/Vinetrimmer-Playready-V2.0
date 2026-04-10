@echo off
python -m pip install poetry
poetry config virtualenvs.in-project true
poetry install
python install_binaries.py
pause