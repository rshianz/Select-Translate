#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f assets/Translator.icns ]; then
  echo "Missing assets/Translator.icns — run the icon steps first."
  exit 1
fi

rm -rf build dist
python3 -m venv .venv-build
source .venv-build/bin/activate
pip install --upgrade pip
pip install -r requirements.txt py2app
python setup.py py2app

echo "Done → dist/Translator.app"