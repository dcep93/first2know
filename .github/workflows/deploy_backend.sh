#!/bin/bash

set -euo pipefail

SA_KEY="$1"
SECRETS_JSON="$2"

cd "$(dirname "$0")"

function c() {
  curl --fail https://chromatic-realm-466116-n0.appspot.com/
}

DIFF="$(git diff HEAD^ ../../backend)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
  c && exit 0 || true
else
  echo "$DIFF"
fi

bash ./record_sha.sh "recorded_sha = '''%s\n%s'''\n" "../../backend/first2know/recorded_sha.py"
bash ./record_secret.sh "$SECRETS_JSON"
bash ./cache_backend_docker.sh
bash ./test_backend.sh
bash ./deploy_to_cloud_run.sh "$SA_KEY"

c || c || c
