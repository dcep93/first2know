#!/bin/bash

set -euo pipefail

SA_KEY="$1"
SECRETS_JSON="$2"

cd "$(dirname "$0")"

function c() {
  curl --fail https://upheld-dragon-453918-n4.appspot.com/
}

DIFF="x$(git diff HEAD^ ../../backend)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
  c && exit 0 || true
else
  echo "$DIFF"
fi

echo "DOCKER_BUILDKIT=1" >> $GITHUB_ENV
echo "CACHE_FROM=type=local,src=/tmp/docker-cache/.buildx-cache" >> $GITHUB_ENV
echo "CACHE_TO=type=local,dest=/tmp/docker-cache/.buildx-cache,mode=max" >> $GITHUB_ENV

bash ./record_sha.sh "recorded_sha = '''%s\n%s'''\n" "../../backend/first2know/recorded_sha.py"
bash ./record_secret.sh "$SECRETS_JSON"
# bash ./test_backend.sh
bash ./deploy_to_app_engine.sh "$SA_KEY"

c || c || c
