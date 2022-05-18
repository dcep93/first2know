#!/bin/bash

set -euo pipefail

cd frontend/first2know
npm install
yarn build
rm -rf node_modules
