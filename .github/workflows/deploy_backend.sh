#!/bin/bash

set -euo pipefail

SA_KEY="$1"
SECRETS_JSON="$2"

cd "$(dirname "$0")"

function c() {
  curl --fail https://upheld-dragon-453918-n4.appspot.com/
}

DIFF="y$(git diff HEAD^ ../../backend)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
  c && exit 0 || true
else
  echo "$DIFF"
fi

bash ./record_sha.sh "recorded_sha = '''%s\n%s'''\n" "../../backend/first2know/recorded_sha.py"
bash ./record_secret.sh "$SECRETS_JSON"
# bash ./test_backend.sh
bash ./deploy_to_app_engine.sh "$SA_KEY"

c || c || c
