# File: deploy_local.sh

#!/bin/bash

echo "🚀 Starting GCP Multi-Agent System Locally..."

# Set project directory
PROJECT_DIR=$(pwd)

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to start agent in background
start_agent() {
    local agent_name=$1
    local port=$2
    
    echo "Starting $agent_name on port $port..."
    cd "$PROJECT_DIR"
    uvicorn agents.${agent_name}.__main__:app --port $port &
    echo $! > ".${agent_name}.pid"
    sleep 3
}

# Check required ports
echo "🔍 Checking available ports..."
for port in 8001 8002 8003 8004 8080; do
    if ! check_port $port; then
        echo "Please free up port $port and try again"
        exit 1
    fi
done

# Start agents in the correct order
echo "🎯 Starting individual agents..."
start_agent "gcp_advisor_agent" 8002
start_agent "architecture_agent" 8003  
start_agent "gcp_management_agent" 8004
start_agent "orchestrator_agent" 8001

# Wait for agents to be ready
echo "⏳ Waiting for agents to initialize..."
sleep 10

# Test agent connectivity
echo "🔍 Testing agent connectivity..."
for port in 8001 8002 8003 8004; do
    if curl -s http://localhost:$port/run -X POST -H "Content-Type: application/json" -d '{"prompt":"health_check"}' > /dev/null 2>&1; then
        echo "✅ Agent on port $port is responding"
    else
        echo "❌ Agent on port $port is not responding"
    fi
done

# Start Chainlit UI
echo "🎨 Starting Chainlit UI..."
export ORCHESTRATOR_URL="http://localhost:8001/run"
chainlit run app.py --port 8080 &
echo $! > ".ui.pid"

echo ""
echo "🎉 GCP Multi-Agent System is running!"
echo "📱 Chainlit UI: http://localhost:8080"
echo "🎯 Orchestrator: http://localhost:8001"
echo "💡 GCP Advisor: http://localhost:8002"
echo "🏗️  Architecture: http://localhost:8003"
echo "⚙️  Management: http://localhost:8004"
echo ""
echo "To stop all services, run: ./stop_local.sh"
