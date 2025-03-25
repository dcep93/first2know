#!/bin/bash

set -euo pipefail

set -x

cd "$(dirname "$0")"

cd ../../backend

docker image ls -a

docker buildx build \
    --load --platform linux/amd64 -t first2know:buildx .


    # --cache-to=type=local,dest=/tmp/github-cache/backend \
    # --cache-from=type=local,src=/tmp/github-cache/backend \

docker image ls -a

make dockerbuild

docker history first2know
