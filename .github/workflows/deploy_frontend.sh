#!/bin/bash

set -euo pipefail

SA_KEY="$1"

cd "$(dirname "$0")"

bash ./record_sha.sh "export const recorded_sha = \`%s\n%s\`;\n" "../../frontend/first2know/src/first2know/recorded_sha.tsx"
bash ./build_react.sh
bash ./deploy_to_firebase.sh "$SA_KEY"
