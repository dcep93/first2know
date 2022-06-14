#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"

cd "$(dirname "$0")"

bash ./record_sha.sh "export const recorded_sha = \`%s\n%s\`;\n" "frontend/first2know/src/first2know/recorded_sha.tsx"
bash ./deploy_to_modal.sh "$MODAL_KEY"
