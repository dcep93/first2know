#!/bin/bash

set -euo pipefail

cd ../../backend

docker buildx build \
    --cache-to=type=local,dest=/tmp/github-cache/backend \
    --cache-from=type=local,src=/tmp/github-cache/backend \
    -t first2know:latest .

make dockerbuild
