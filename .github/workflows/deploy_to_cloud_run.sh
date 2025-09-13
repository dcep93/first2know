#!/bin/bash

set -euo pipefail

# # requires billing!
# # create a new project every 3 months once trial expires
# # first2know20250716@cloudshell:~
# # chromatic-realm-466116-n0 # todo infer project_id from json
# set -e
# nvm install 16.4.0
# gcloud services enable compute
# gcloud services enable cloudbuild.googleapis.com
# gcloud services enable run.googleapis.com
# IAM=deployer-github-cloudrun1
# gcloud iam service-accounts create $IAM
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/run.admin"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.editor"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/storage.objectViewer"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/editor"
# gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" --member="serviceAccount:$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" --role="roles/viewer"
# gcloud iam service-accounts keys create gac.json --iam-account "$IAM@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com"
# cat gac.json

SA_KEY="$1"

REGION="us-east1"

export GOOGLE_APPLICATION_CREDENTIALS="gac.json"
echo "$SA_KEY" >"$GOOGLE_APPLICATION_CREDENTIALS"
npm install google-auth-library
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
GOOGLE_CLOUD_PROJECT="$(jq -r .project_id < "$GOOGLE_APPLICATION_CREDENTIALS")"

cd ../../backend
echo 'ENTRYPOINT [ "make", "server" ]' >>Dockerfile

gcloud config set builds/use_kaniko True
gcloud config set builds/kaniko_cache_ttl 8760
IMG_URL=us.gcr.io/"${GOOGLE_CLOUD_PROJECT}"/first2know/backend:"$(git log -1 --format=format:%H)"
IMG_URL=us.gcr.io/"${GOOGLE_CLOUD_PROJECT}"/first2know/backend:"faf9f678e8be1d4df65c2e94d8f5b765aec1d488"
# gcloud builds submit --project "${GOOGLE_CLOUD_PROJECT}" --tag "${IMG_URL}"

echo deploying $GOOGLE_CLOUD_PROJECT cloudrun

gcloud run deploy "first2know" \
  --project "${GOOGLE_CLOUD_PROJECT}" \
  --region "${REGION}" \
  --image "${IMG_URL}" \
  --platform managed \
  --allow-unauthenticated \
  --cpu 4 \
  --memory 6Gi \
  --min-instances 1 \
  --max-instances 1 \
  --timeout 300

# # gsutil -m rm -r "gs://us.artifacts.${GOOGLE_CLOUD_PROJECT}.appspot.com"
# # gcloud beta app repair
