#!/bin/bash

set -euo pipefail

# # requires billing!
# # first2know20240904@cloudshell:~
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

SA_KEY="$1"
SECRETS_JSON="$2"

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

resources:
  cpu: 2
  memory_gb: 4

manual_scaling:
  instances: 1

EOF
echo 'ENTRYPOINT [ "make", "server" ]' >>Dockerfile
echo "$SECRETS_JSON" >first2know/secrets.json
gcloud config set builds/use_kaniko True
gcloud config set builds/kaniko_cache_ttl 8760
IMG_URL=us.gcr.io/"${GOOGLE_CLOUD_PROJECT}"/first2know/backend:"$(git log -1 --format=format:%H)"
gcloud builds submit --project "${GOOGLE_CLOUD_PROJECT}" --tag "${IMG_URL}"
gcloud app deploy --project "${GOOGLE_CLOUD_PROJECT}" --version 1 --image-url="${IMG_URL}"
# # gsutil -m rm -r "gs://us.artifacts.${GOOGLE_CLOUD_PROJECT}.appspot.com"
# # gcloud beta app repair
