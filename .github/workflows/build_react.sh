#!/bin/bash

set -euo pipefail

cd ../../frontend/first2know
git diff .
echo hi
exit 1
npm install
yarn build
rm -rf node_modules
