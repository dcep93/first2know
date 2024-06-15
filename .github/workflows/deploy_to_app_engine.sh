#!/bin/bash

set -euo pipefail

# # requires billing!
# # first2know20240615
# # enable api https://console.developers.google.com/apis/api/appengine.googleapis.com/overview
# # enable cloud build https://console.cloud.google.com/apis/library/cloudbuild.googleapis.com
# nvm install 16.4.0
# gcloud app create --project "$GOOGLE_CLOUD_PROJECT" --region us-east1
# gcloud iam service-accounts create deployer-github
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/appengine.appAdmin"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.editor"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/editor"
# gcloud iam service-accounts keys create gac.json --iam-account "deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com"
# cat gac.json

cd ../../backend
export GOOGLE_APPLICATION_CREDENTIALS="gac.json"
echo "$1" >"$GOOGLE_APPLICATION_CREDENTIALS"
npm install google-auth-library
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
GOOGLE_CLOUD_PROJECT="$(cat $GOOGLE_APPLICATION_CREDENTIALS | jq -r .project_id)"
cat <<EOF >app.yaml
runtime: custom
env: flex
automatic_scaling:
  min_num_instances: 1
  max_num_instances: 1

EOF
gcloud app deploy --project "${GOOGLE_CLOUD_PROJECT}" --version 1 --no-cache
gsutil -m rm -r "gs://us.artifacts.${GOOGLE_CLOUD_PROJECT}.appspot.com"
# gcloud beta app repair
