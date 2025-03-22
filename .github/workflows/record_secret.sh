#!/bin/bash

set -euo pipefail

SECRETS_JSON="$1"

cd ../../backend

echo "$SECRETS_JSON" >first2know/secrets.json
