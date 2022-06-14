#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"
# TWITTER_KEY="$2"

bash ./install_modal "$MODAL_KEY"

cd ../../cron/first2know
modal app deploy --name first2know_cron modal_app.py:modal_app
