#!/bin/bash

set -euo pipefail

SA_KEY="$1"
SECRETS_JSON="$2"

cd "$(dirname "$0")"

DIFF="x$(git diff HEAD^ ../../backend/first2know)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
else
  echo "$DIFF"
  bash ./record_sha.sh "recorded_sha = '''%s\n%s'''\n" "../../backend/first2know/recorded_sha.py"
  bash ./deploy_to_app_engine.sh "$SA_KEY" "$SECRETS_JSON"
fi

function c() {
  curl --fail https://first2know20240615.appspot.com/
}

c || c || c
