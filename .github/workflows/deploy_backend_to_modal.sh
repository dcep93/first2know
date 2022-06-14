#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"

bash ./install_modal.sh "$MODAL_KEY"

cd ../../backend/first2know
modal app deploy --name=first2know_server modal_app.py:modal_app
