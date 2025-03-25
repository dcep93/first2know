#!/bin/bash

set -euo pipefail

set -x

cd "$(dirname "$0")"

cd ../../backend

docker image ls -a

docker buildx build \
    --cache-to=type=local,dest=/tmp/github-cache/backend \
    --cache-from=type=local,src=/tmp/github-cache/backend \
    --load --platform linux/amd64 -t first2know:buildx .

docker image ls -a

echo make dockerbuild1
make dockerbuild
echo make dockerbuild2
make dockerbuild

docker image ls -a

docker history first2know
