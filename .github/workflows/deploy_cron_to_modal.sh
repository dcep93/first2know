#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"
# TWITTER_KEY="$2"

TOKEN_ID="ak-38vXak6m5VJheg1cvrKQul"
MODAL_PIP_URL="https://modal.com/api/client-library/us-JOXmaxhr5FVrM66sBK1J29/modal-0.0.15-py3-none-any.whl"

pip install "$MODAL_PIP_URL"
modal token set --token-id "$TOKEN_ID" --token-secret "$MODAL_KEY"

cd ../../cron/first2know
modal app deploy --name first2know_cron modal_app.py:modal_app
