#!/bin/bash

set -euo pipefail

FMT="$1"
DESTINATION="$2"

CURRENT_TIME="$(TZ='America/Los_Angeles' date)"
GIT_LOG="$(git log -1)"

test -f "$DESTINATION"
# shellcheck disable=2059
printf "$FMT" "$CURRENT_TIME" "$GIT_LOG" > "$DESTINATION"
cat "$DESTINATION"
