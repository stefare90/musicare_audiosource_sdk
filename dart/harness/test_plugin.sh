#!/bin/bash
set -e

PLUGIN_ZIP=$1
DEVICE=${2:-linux}

if [ -z "$PLUGIN_ZIP" ]; then
  echo "❌ Error: Missing plugin.zip argument."
  echo "👉 Usage: ./test_plugin.sh <path_to_plugin.zip> [device_id]"
  exit 1
fi

PLUGIN_ZIP_ABS=$(realpath "$PLUGIN_ZIP")

if [ ! -f "$PLUGIN_ZIP_ABS" ]; then
  echo "❌ Error: File '$PLUGIN_ZIP_ABS' does not exist."
  exit 1
fi

PORT=8888

# 🎯 1. Avvia il server HTTP nativo in DART (zero dipendenze esterne!)
dart run tool/serve_file.dart "$PLUGIN_ZIP_ABS" $PORT &
HTTP_PID=$!

# Assicura che il server Dart venga terminato all'uscita
trap "kill $HTTP_PID 2>/dev/null || true; adb -s $DEVICE reverse --remove-all 2>/dev/null || true" EXIT

# Attendi mezzo secondo che il server Dart sia in ascolto
sleep 0.5

PLATFORM="Linux"
if [ "$DEVICE" != "linux" ]; then
  PLATFORM="Android"
  # Inoltra la porta 8888 dal telefono al PC
  adb -s "$DEVICE" reverse tcp:$PORT tcp:$PORT
fi

echo "=================================================="
echo "1. Staging SeriousPython Host Runtime ($PLATFORM)"
echo "=================================================="
rm -rf build/python-app build/site-packages build/host_staging
mkdir -p build/python-app build/site-packages build/host_staging

# Copia i sorgenti dell'Host e dell'SDK nella cartella di staging
cp -r ../../python/host_runtime/* build/host_staging/
cp -r ../../python/plugin_sdk/musicare_plugin_sdk build/host_staging/

export SERIOUS_PYTHON_SITE_PACKAGES=$(pwd)/build/site-packages
export SERIOUS_PYTHON_APP=$(pwd)/build/python-app

# SeriousPython pacchettizza l'host
dart run serious_python:main package build/host_staging \
  -p $PLATFORM \
  -r -r -r ../../python/host_runtime/requirements.txt \
  --compile-packages \
  --cleanup-packages

echo "=================================================="
echo "2. Running Compliance Test on '$DEVICE'..."
echo "=================================================="
flutter test -d "$DEVICE" integration_test/verify_plugin_test.dart \
  --dart-define=PLUGIN_URL="http://127.0.0.1:$PORT/plugin.zip"