#!/bin/bash

# This script lists and (optionally) deletes all Cloud Run services in the specified project and region.
# Use with caution!

PROJECT_ID="gcp-cloud-agent-testing-2025"
REGION="us-central1"

set -e

echo "🔍 Listing all Cloud Run services in project: $PROJECT_ID, region: $REGION"

gcloud run services list --platform managed --region $REGION --project $PROJECT_ID --format="table(metadata.name,status.url)"

SERVICES=$(gcloud run services list --platform managed --region $REGION --project $PROJECT_ID --format="value(metadata.name)")

if [ -z "$SERVICES" ]; then
  echo "✅ No Cloud Run services found to delete."
  exit 0
fi

echo "\n⚠️  The above services will be deleted."
echo -n "Type 'yes' to confirm deletion, or anything else to cancel: "
read CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "❌ Deletion cancelled. No services were deleted."
  exit 0
fi

for svc in $SERVICES; do
  echo "Deleting service: $svc ..."
  gcloud run services delete $svc --platform managed --region $REGION --project $PROJECT_ID --quiet
done

echo "✅ All Cloud Run services deleted."

gcloud run services list --platform managed --region us-central1 --project gcp-cloud-agent-testing-2025 