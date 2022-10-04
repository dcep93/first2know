#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"
SECRETS_JSON="$2"

TOKEN_ID="ak-38vXak6m5VJheg1cvrKQul"

pip install modal-client
modal token set --token-id "$TOKEN_ID" --token-secret "$MODAL_KEY"

cd ../../backend
modal secret create "first2know_s" secrets.json="$SECRETS_JSON"

make modaldeploy || make modaldeploy || make modaldeploy
