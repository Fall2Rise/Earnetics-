#!/bin/bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
(cd fallat_crewai_dashboard && npm install && npm run build)
