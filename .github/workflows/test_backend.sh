#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

#

cd ../../backend

ARGS=mypy make dockerexecnotty
ARGS=test make dockerexecnotty
