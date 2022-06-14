#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"
TWITTER_KEY="$2"

cd "$(dirname "$0")"

DIFF="$(git diff HEAD^ ../../cron/first2know)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
else
  echo "$DIFF"
  bash ./record_sha.sh "recorded_sha = '''%s\n%s'''\n" "../../cron/first2know/recorded_sha.py"
  bash ./deploy_cron_to_modal.sh "$MODAL_KEY" "$TWITTER_KEY"
fi
