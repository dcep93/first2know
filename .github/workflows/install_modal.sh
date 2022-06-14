#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"

TOKEN_ID="ak-38vXak6m5VJheg1cvrKQul"
# TODO dcep93
MODAL_PIP_URL="https://modal.com/api/client-library/us-JOXmaxhr5FVrM66sBK1J29/modal-0.0.16-py3-none-any.whl"

pip install "$MODAL_PIP_URL"
modal token set --token-id "$TOKEN_ID" --token-secret "$MODAL_KEY"
