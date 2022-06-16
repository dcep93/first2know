#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"
# TODO dcep93 - save to modal
# TWITTER_KEY="$2"

TOKEN_ID="ak-38vXak6m5VJheg1cvrKQul"
# TODO dcep93 - constant url
MODAL_PIP_URL="https://modal.com/api/client-library/us-JOXmaxhr5FVrM66sBK1J29/modal-0.0.16-py3-none-any.whl"

pip install "$MODAL_PIP_URL"
modal token set --token-id "$TOKEN_ID" --token-secret "$MODAL_KEY"

cd ../../backend/first2know
modal app deploy --name=first2know modal_app.py:modal_app
