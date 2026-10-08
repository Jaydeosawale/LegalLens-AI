#!/usr/bin/env bash
set -euo pipefail

: "${API_BASE_URL:?Set API_BASE_URL to the HTTPS URL of the Render API}"

FLUTTER_DIR="${HOME}/flutter"
if [ ! -x "${FLUTTER_DIR}/bin/flutter" ]; then
  git clone --depth 1 --branch 3.47.2 https://github.com/flutter/flutter.git "${FLUTTER_DIR}"
fi

cd frontend
"${FLUTTER_DIR}/bin/flutter" pub get
"${FLUTTER_DIR}/bin/flutter" build web --release \
  --dart-define="API_BASE_URL=${API_BASE_URL%/}"
