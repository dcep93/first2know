#!/bin/bash

set -euo pipefail

MODAL_KEY="$1"

echo "TODO $MODAL_KEY TODO"

pip install --force-reinstall https://modal.com/api/client-library/us-JOXmaxhr5FVrM66sBK1J29/modal-0.0.15-py3-none-any.whl

exit 0

cd backend/first2know
modal app deploy screenshot.py:modal_app --name=first2know

curl https://dcep93-first2know-app.modal.run/warm
curl https://dcep93-first2know-app.modal.run/echo/https://chess.com
