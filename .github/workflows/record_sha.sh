#!/bin/bash

set -euo pipefail

CURRENT_TIME="$(TZ='America/Los_Angeles' date)"
GIT_LOG="$(git log -1)"

frontend_filename=frontend/first2know/src/first2know/recorded_sha.tsx
test -f "$frontend_filename"
printf "export const recorded_sha = \`%s\n%s\`;\n" "$CURRENT_TIME" "$GIT_LOG" > "$frontend_filename"

backend_filename=backend/first2know/recorded_sha.py
test -f "$backend_filename"
printf "recorded_sha = '''%s\n%s'''\n" "$CURRENT_TIME" "$GIT_LOG" > "$backend_filename"
