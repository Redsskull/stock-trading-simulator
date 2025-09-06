#!/usr/bin/env bash
set -e

echo "Upgrading pip3..."
pip3 install --upgrade pip

echo "Installing dependencies with pip3..."
pip3 install -r requirements.txt

echo "Build completed successfully."
