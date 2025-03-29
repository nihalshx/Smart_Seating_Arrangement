#!/bin/bash

# Ensure pip is up to date
pip install --upgrade pip setuptools wheel

# Install core dependencies first
pip install -c constraints.txt flask python-dotenv werkzeug

# Install the rest of the dependencies
pip install -r requirements.txt --no-cache-dir -c constraints.txt 