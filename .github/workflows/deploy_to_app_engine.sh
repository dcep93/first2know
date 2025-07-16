#!/bin/bash

set -euo pipefail

# # requires billing!
# # create a new project every 3 months once trial expires
# # first2know20250316@cloudshell:~
# # chromatic-realm-466116-n0 # todo infer project_id from json
# set -e
# nvm install 16.4.0
# gcloud services enable compute
# gcloud services enable appengine
# gcloud services enable cloudbuild.googleapis.com
# gcloud app create --project "$GOOGLE_CLOUD_PROJECT" --region us-east1
# gcloud iam service-accounts create deployer-github
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/appengine.appAdmin"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.editor"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/editor"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/viewer"
# gcloud iam service-accounts keys create gac.json --iam-account "deployer-github@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com"
# cat gac.json

SA_KEY="$1"

export GOOGLE_APPLICATION_CREDENTIALS="gac.json"
echo "$SA_KEY" >"$GOOGLE_APPLICATION_CREDENTIALS"
npm install google-auth-library
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
GOOGLE_CLOUD_PROJECT="$(cat $GOOGLE_APPLICATION_CREDENTIALS | jq -r .project_id)"

cd ../../backend
cat <<EOF >app.yaml
runtime: custom
env: flex

liveness_check:
  path: "/liveness_check"
  failure_threshold: 8

resources:
  cpu: 2
  memory_gb: 4

manual_scaling:
  instances: 1

EOF
echo 'ENTRYPOINT [ "make", "server" ]' >>Dockerfile
gcloud config set builds/use_kaniko True
gcloud config set builds/kaniko_cache_ttl 8760
IMG_URL=us.gcr.io/"${GOOGLE_CLOUD_PROJECT}"/first2know/backend:"$(git log -1 --format=format:%H)"
gcloud builds submit --project "${GOOGLE_CLOUD_PROJECT}" --tag "${IMG_URL}"
gcloud app deploy --project "${GOOGLE_CLOUD_PROJECT}" --version 1 --image-url="${IMG_URL}"
# # gsutil -m rm -r "gs://us.artifacts.${GOOGLE_CLOUD_PROJECT}.appspot.com"
# # gcloud beta app repair
