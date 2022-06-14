#!/bin/bash

set -euo pipefail

SA_KEY="$1"

# firebase init hosting --project first2know
# gcloud iam service-accounts create firebase-deployer-github
# gcloud projects add-iam-policy-binding first2know --member="serviceAccount:firebase-deployer-github@first2know.iam.gserviceaccount.com" --role="roles/firebasehosting.admin"
# gcloud iam service-accounts keys create gac.json --iam-account firebase-deployer-github@first2know.iam.gserviceaccount.com
# cat gac.json

cd frontend/first2know
export GOOGLE_APPLICATION_CREDENTIALS="gac.json"
echo "$SA_KEY" > "$GOOGLE_APPLICATION_CREDENTIALS"
npm install -g firebase-tools
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
firebase deploy --project "$(cat $GOOGLE_APPLICATION_CREDENTIALS | jq -r .project_id)"
