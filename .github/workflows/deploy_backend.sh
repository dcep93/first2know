#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"
SECRETS_JSON="$2"

cd "$(dirname "$0")"

DIFF="$(git diff HEAD^ ../../backend/first2know)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
else
  echo "$DIFF"
  bash ./record_sha.sh "recorded_sha = '''%s\n%s'''\n" "../../backend/first2know/recorded_sha.py"
  bash ./deploy_to_modal.sh "$MODAL_KEY" "$SECRETS_JSON"
fi

function c() {
  curl --fail https://dcep93--first2know-app.modal.run/
}

c || c || c
