#!/bin/bash

set -e

# Configuration
PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION="us-central1"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Please provide PROJECT_ID as argument or set it in gcloud config"
    echo "Usage: ./deploy_cloud.sh YOUR_PROJECT_ID"
    exit 1
fi

echo "🚀 Deploying GCP Multi-Agent System to Cloud Run..."
echo "📍 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

# Build and deploy agents in correct order (individual agents first, then orchestrator)
echo "🏗️  Building and deploying individual agents..."

echo "📦 1/5 Deploying GCP Advisor Agent..."
if gcloud builds submit --config cloudbuild-gcp-advisor.yaml --project=$PROJECT_ID; then
    echo "✅ GCP Advisor Agent deployed successfully"
else
    echo "❌ GCP Advisor Agent deployment failed"
    exit 1
fi

echo "📦 2/5 Deploying Architecture Agent..."
if gcloud builds submit --config cloudbuild-architecture.yaml --project=$PROJECT_ID; then
    echo "✅ Architecture Agent deployed successfully"
else
    echo "❌ Architecture Agent deployment failed"
    exit 1
fi

echo "📦 3/5 Deploying GCP Management Agent..."
if gcloud builds submit --config cloudbuild-gcp-management.yaml --project=$PROJECT_ID; then
    echo "✅ GCP Management Agent deployed successfully"
else
    echo "❌ GCP Management Agent deployment failed"
    exit 1
fi

# Wait a moment for services to be ready
echo "⏳ Waiting for individual agents to be ready..."
sleep 30

# Get service URLs for orchestrator environment variables
echo "🔍 Getting service URLs..."
GCP_ADVISOR_URL=$(gcloud run services describe gcp-advisor-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)
ARCHITECTURE_URL=$(gcloud run services describe architecture-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)
GCP_MANAGEMENT_URL=$(gcloud run services describe gcp-management-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)

# Check if URLs were retrieved successfully
if [ -z "$GCP_ADVISOR_URL" ] || [ -z "$ARCHITECTURE_URL" ] || [ -z "$GCP_MANAGEMENT_URL" ]; then
    echo "❌ Failed to get service URLs. Checking individual services..."
    echo "GCP Advisor URL: $GCP_ADVISOR_URL"
    echo "Architecture URL: $ARCHITECTURE_URL"
    echo "GCP Management URL: $GCP_MANAGEMENT_URL"
    exit 1
fi

# Add /run to the URLs
GCP_ADVISOR_URL="${GCP_ADVISOR_URL}/run"
ARCHITECTURE_URL="${ARCHITECTURE_URL}/run"
GCP_MANAGEMENT_URL="${GCP_MANAGEMENT_URL}/run"

echo "🔗 Agent URLs:"
echo "   GCP Advisor: $GCP_ADVISOR_URL"
echo "   Architecture: $ARCHITECTURE_URL"
echo "   GCP Management: $GCP_MANAGEMENT_URL"

# Deploy orchestrator with agent URLs
echo "📦 4/5 Deploying Orchestrator Agent..."
if gcloud builds submit --config cloudbuild-orchestrator.yaml --project=$PROJECT_ID; then
    echo "✅ Orchestrator Agent deployed successfully"
else
    echo "❌ Orchestrator Agent deployment failed"
    exit 1
fi

# Update orchestrator with correct environment variables
echo "🔧 Updating orchestrator environment variables..."
if gcloud run services update orchestrator-agent \
    --region=$REGION \
    --project=$PROJECT_ID \
    --set-env-vars="GCP_ADVISOR_URL=$GCP_ADVISOR_URL,ARCHITECTURE_URL=$ARCHITECTURE_URL,GCP_MANAGEMENT_URL=$GCP_MANAGEMENT_URL"; then
    echo "✅ Orchestrator environment variables updated"
else
    echo "❌ Failed to update orchestrator environment variables"
    exit 1
fi

# Wait for orchestrator to be ready
echo "⏳ Waiting for orchestrator to be ready..."
sleep 15

# Get orchestrator URL for UI
ORCHESTRATOR_URL=$(gcloud run services describe orchestrator-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)

if [ -z "$ORCHESTRATOR_URL" ]; then
    echo "❌ Failed to get orchestrator URL"
    exit 1
fi

ORCHESTRATOR_URL="${ORCHESTRATOR_URL}/run"
echo "🔗 Orchestrator URL: $ORCHESTRATOR_URL"

# Deploy UI
echo "📦 5/5 Deploying Chainlit UI..."
if gcloud builds submit --config cloudbuild-ui.yaml --project=$PROJECT_ID; then
    echo "✅ Chainlit UI deployed successfully"
else
    echo "❌ Chainlit UI deployment failed"
    exit 1
fi

# Update UI with orchestrator URL
echo "🔧 Updating UI environment variables..."
if gcloud run services update gcp-multi-agent-ui \
    --region=$REGION \
    --project=$PROJECT_ID \
    --set-env-vars="ORCHESTRATOR_URL=$ORCHESTRATOR_URL"; then
    echo "✅ UI environment variables updated"
else
    echo "❌ Failed to update UI environment variables"
    exit 1
fi

# Test connectivity with better error handling
echo "🧪 Testing agent connectivity..."
sleep 10

test_service() {
    local service=$1
    local url=$(gcloud run services describe $service --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)
    
    if [ -z "$url" ]; then
        echo "⚠️  $service: Could not get service URL"
        return 1
    fi
    
    if curl -s -X POST "$url/run" --connect-timeout 10 --max-time 30 \
        -H "Content-Type: application/json" \
        -d '{"prompt":"health_check"}' > /dev/null 2>&1; then
        echo "✅ $service is responding at $url"
        return 0
    else
        echo "⚠️  $service may need more time to start (URL: $url)"
        return 1
    fi
}

# Test each service
services=("gcp-advisor-agent" "architecture-agent" "gcp-management-agent" "orchestrator-agent")
failed_services=()

for service in "${services[@]}"; do
    if ! test_service $service; then
        failed_services+=($service)
    fi
done

# Report connectivity results
if [ ${#failed_services[@]} -eq 0 ]; then
    echo "✅ All services are responding!"
else
    echo "⚠️  Some services may need more time: ${failed_services[*]}"
    echo "🔄 This is normal for initial deployment. Services should be available shortly."
fi

# Get final URLs
echo ""
echo "🎉 Deployment completed successfully!"
echo ""

# Get and display all service URLs
UI_URL=$(gcloud run services describe gcp-multi-agent-ui --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)
ORCHESTRATOR_BASE_URL=$(gcloud run services describe orchestrator-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)
ADVISOR_BASE_URL=$(gcloud run services describe gcp-advisor-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)
ARCHITECTURE_BASE_URL=$(gcloud run services describe architecture-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)
MANAGEMENT_BASE_URL=$(gcloud run services describe gcp-management-agent --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null)

echo "📱 **Chainlit UI (Main App):** $UI_URL"
echo "🎯 **Orchestrator:** $ORCHESTRATOR_BASE_URL"
echo "💡 **GCP Advisor:** $ADVISOR_BASE_URL"
echo "🏗️  **Architecture:** $ARCHITECTURE_BASE_URL"
echo "⚙️  **Management:** $MANAGEMENT_BASE_URL"
echo ""
echo "🌟 **START HERE:** Open the Chainlit UI to interact with your multi-agent system!"
echo "🔗 **Main URL:** $UI_URL"
echo ""
echo "✅ All services are now running on Google Cloud Run!"
echo "🔄 Services will auto-scale based on demand and scale to zero when not in use."
echo "💰 You only pay for actual usage - services scale to zero when idle."
echo ""
echo "📝 **Next Steps:**"
echo "   1. Open the Chainlit UI URL above"
echo "   2. Test with: 'I want to create a storage bucket'"
echo "   3. Try: 'Design an architecture for a web application'"
echo "   4. Ask: 'Recommend GCP services for my startup'"