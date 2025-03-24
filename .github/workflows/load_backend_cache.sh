#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

cd ../../backend

mkdir -p /tmp/github-cache
ls -lah /tmp/github-cache || true

docker image ls -a

docker buildx build --cache-to=type=local,dest=/tmp/github-cache --cache-from=type=local,src=/tmp/github-cache --load .

echo asdfasdf

docker image ls -a

make dockerbuild

rm /tmp/github-cache/butt* || true

touch "/tmp/github-cache/butt_$(date +%s)"

# docker save -o /tmp/github-cache/backend.tar first2know:latest
ls -lah /tmp/github-cache || true