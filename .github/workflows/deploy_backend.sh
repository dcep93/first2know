#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"

cd "$(dirname "$0")"

DIFF="$(git diff HEAD^ ../../backend/first2know)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
  exit 0
fi
bash ./record_sha.sh "export const recorded_sha = \`%s\n%s\`;\n" "frontend/first2know/src/first2know/recorded_sha.tsx"
bash ./deploy_to_modal.sh "$MODAL_KEY"
