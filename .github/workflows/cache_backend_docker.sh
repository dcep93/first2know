#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

cd ../../backend

docker image ls -a

docker buildx build \
    --cache-to=type=local,dest=/tmp/github-cache/backend \
    --cache-from=type=local,src=/tmp/github-cache/backend \
    --load --platform linux/amd64 -t first2know:latest .

docker history first2know

echo asdfasdf

docker image ls -a

make dockerbuild

ls -lah /tmp/github-cache || true
