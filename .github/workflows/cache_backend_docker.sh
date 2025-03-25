#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

cd ../../backend

docker image ls -a

docker buildx build \
    --cache-to=type=local,dest=/tmp/github-cache \
    --cache-from=type=local,src=/tmp/github-cache \
    --load .

echo asdfasdf

docker image ls -a

make dockerbuild

ls -lah /tmp/github-cache || true
