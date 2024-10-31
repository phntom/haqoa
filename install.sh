#!/usr/bin/env bash
set -ex
python3 -m venv .venv || (sudo apt install python3.10-venv && python3 -m venv .venv)
./.venv/bin/pip install -r requirements.txt
