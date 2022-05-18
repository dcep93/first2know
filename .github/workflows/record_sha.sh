#!/bin/bash

set -euo pipefail

filename=src/first2know/recorded_sha.tsx

cd frontend/first2know
test -f "$filename"
printf "export const recorded_sha = \`%s\n%s\`;\n" "$(TZ='America/Los_Angeles' date)" "$(git log -1)" > "$filename"
