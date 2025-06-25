#!/bin/bash

PROJECT_ID="gcp-cloud-agent-testing-2025"

echo "🚀 Quick Chainlit Deployment"

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --project=$PROJECT_ID

# Deploy directly
gcloud run deploy gcp-multi-agent-ui \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --project $PROJECT_ID

# Get URL
URL=$(gcloud run services describe gcp-multi-agent-ui --region=us-central1 --project=$PROJECT_ID --format="value(status.url)")

echo ""
echo "🎉 SUCCESS! Your Chainlit UI is live:"
echo "🔗 $URL"
echo "📌 This URL is permanent and ready for submission!"