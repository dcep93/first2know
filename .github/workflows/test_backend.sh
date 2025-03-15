#!/bin/bash

set -euo pipefail

ARGS=mypy make dockerexec
ARGS=test make dockerexec
