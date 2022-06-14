#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"

cd "$(dirname "$0")"

DIFF="$(git diff HEAD^ ../../backend/first2know)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
else
  echo "$DIFF"
  bash ./record_sha.sh "recorded_sha = '''%s\n%s'''\n" "../../backend/first2know/recorded_sha.py"
  bash ./deploy_backend_to_modal.sh "$MODAL_KEY"
fi

curl --fail https://dcep93-first2know-server-app.modal.run/
