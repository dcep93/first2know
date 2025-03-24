#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

cd ../../backend

mkdir -p /tmp/github-cache
ls -lah /tmp/github-cache || true

docker buildx build --cache-to=type=registry,ref=myrepo/myimage-cache --tag myimage --push . || echo failed

rm /tmp/github-cache/*

docker image ls

make dockerbuild

# docker save -o /tmp/github-cache/backend.tar first2know:latest
ls -lah /tmp/github-cache || true