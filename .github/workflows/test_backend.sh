#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

#

ARGS=mypy make dockerexec
ARGS=test make dockerexec
