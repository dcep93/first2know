#!/bin/bash

set -euo pipefail

cd ../../backend

mkdir -p /tmp/github-cache
ls -lah /tmp/github-cache || true
test ! -f /tmp/github-cache/backend.tar || (docker load -i /tmp/github-cache/backend.tar && echo loaded)
make dockerbuild
make dockerbuild
docker save -o /tmp/github-cache/backend.tar first2know:latest
ls -lah /tmp/github-cache || true