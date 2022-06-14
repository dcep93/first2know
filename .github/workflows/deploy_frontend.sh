#!/bin/bash

set -euo pipefail

SA_KEY="$1"

cd "$(dirname "$0")"

git log
DIFF="$(git diff HEAD^ ../../frontend/first2know)"
if [[ -z "$DIFF" ]]; then
  echo "no diff"
  exit 0
fi
bash ./record_sha.sh "export const recorded_sha = \`%s\n%s\`;\n" "../../frontend/first2know/src/first2know/recorded_sha.tsx"
bash ./build_react.sh
bash ./deploy_to_firebase.sh "$SA_KEY"
