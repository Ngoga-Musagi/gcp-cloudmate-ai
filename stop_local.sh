# File: stop_local.sh

#!/bin/bash

echo "🛑 Stopping GCP Multi-Agent System..."

# Kill agents using PID files
for agent in gcp_advisor_agent architecture_agent gcp_management_agent orchestrator_agent ui; do
    if [ -f ".${agent}.pid" ]; then
        pid=$(cat ".${agent}.pid")
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping $agent (PID: $pid)..."
            kill $pid
        fi
        rm ".${agent}.pid"
    fi
done

# Kill any remaining processes on our ports
for port in 8001 8002 8003 8004 8080; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null
    fi
done

echo "✅ All services stopped!"