# 🌟 GCP CloudMate AI

**Tagline:** *Let your ideas meet the cloud—instantly, intelligently, and effortlessly manage it—with GCP CloudMate AI.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com)

## 🚀 Overview

GCP CloudMate AI is an **AI-powered, multi-agent assistant** that revolutionizes how you interact with Google Cloud Platform. Instead of navigating complex dashboards and CLI commands, simply describe what you want in natural language, and let our intelligent agents handle the technical complexity.

### ✨ What It Does

Transform cloud management into natural conversations:

- 💡 **Smart Recommendations**: Get personalized GCP service suggestions based on your goals and budget
- 🏗️ **Instant Architecture**: Generate complete system architectures from simple requirements  
- ⚙️ **Resource Management**: Create, manage, and delete GCP resources like Firestore databases and Cloud Storage buckets
- 🎨 **Visual Diagrams**: Automatically generate PlantUML architecture diagrams
- 💬 **Natural Language**: No technical jargon required—just describe what you need

### 🤖 Multi-Agent Architecture

GCP CloudMate AI uses specialized AI agents that work together:

| Agent | Purpose | Capabilities |
|-------|---------|-------------|
| **🎯 Orchestrator** | Coordinates all agents and routes user requests | Session management, intelligent routing |
| **💡 GCP Advisor** | Provides service recommendations and cost estimates | Service selection, budget analysis, compliance guidance |
| **🏗️ Architecture** | Designs system architectures and creates diagrams | System design, PlantUML diagrams, scalability planning |
| **⚙️ Management** | Handles actual GCP resource operations | Resource creation/deletion, configuration management |

## 🎬 Demo Examples

### Example 1: Get Service Recommendations
```
👤 User: "I'm building a scalable e-commerce platform with a $5,000/month budget"

🤖 CloudMate: Recommends Cloud Run for APIs, Cloud SQL for transactions, 
Cloud Storage for assets, and provides detailed cost breakdown
```

### Example 2: Generate Architecture
```
👤 User: "Design a video analytics pipeline for processing user uploads"

🤖 CloudMate: Creates complete architecture with Cloud Storage, 
Cloud Functions, AI Platform, and generates visual PlantUML diagram
```

### Example 3: Manage Resources
```
👤 User: "Create a storage bucket called 'my-app-data' in us-central1"

🤖 CloudMate: Creates the bucket with optimal settings and confirms success
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Chainlit UI   │───▶│   Orchestrator   │───▶│   Specialized       │
│  (Frontend)     │    │     Agent        │    │     Agents          │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────────┐
                       │ Session Manager │    │  ┌─────────────────┐ │
                       │ (Context &      │    │  │ GCP Advisor     │ │
                       │  Continuity)    │    │  │ Architecture    │ │
                       └─────────────────┘    │  │ Management      │ │
                                              │  └─────────────────┘ │
                                              └─────────────────────┘
```

## 📋 Prerequisites

- **Python 3.11+**
- **Google Cloud SDK** installed and configured
- **Docker** (for containerized deployment)
- **Google Cloud Project** with billing enabled
- **API Keys**: Google AI API key or Vertex AI access

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/gcp-cloudmate-ai.git
cd gcp-cloudmate-ai
```

### 2. Set Up Environment
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Option 1: Set environment variable
export GOOGLE_API_KEY="your_google_ai_api_key"

# Option 2: Create .env files for each agent (recommended)
echo "GOOGLE_API_KEY=your_api_key_here" > agents/orchestrator_agent/.env
echo "GOOGLE_API_KEY=your_api_key_here" > agents/gcp_advisor_agent/.env
echo "GOOGLE_API_KEY=your_api_key_here" > agents/architecture_agent/.env
echo "GOOGLE_API_KEY=your_api_key_here" > agents/gcp_management_agent/.env
```

## 🖥️ Local Development

### Run Locally
```bash
# Make script executable
chmod +x deploy_local.sh

# Start all services locally
./deploy_local.sh
```

This will start:
- 🎯 Orchestrator Agent: `http://localhost:8001`
- 💡 GCP Advisor Agent: `http://localhost:8002`  
- 🏗️ Architecture Agent: `http://localhost:8003`
- ⚙️ Management Agent: `http://localhost:8004`
- 💬 Chainlit UI: `http://localhost:8080`

### Stop Local Services
```bash
./stop_local.sh
```

## ☁️ Cloud Deployment

### Deploy to Google Cloud Run
```bash
# Make script executable
chmod +x deploy_cloud.sh

# Deploy to your GCP project
./deploy_cloud.sh YOUR_PROJECT_ID
```

### Example:
```bash
./deploy_cloud.sh gcp-cloud-agent-testing-2025
```

After deployment, you'll get URLs for all services:
- 📱 **Main UI**: `https://gcp-multi-agent-ui-[hash].us-central1.run.app`
- 🎯 **Orchestrator**: `https://orchestrator-agent-[hash].us-central1.run.app`
- 💡 **GCP Advisor**: `https://gcp-advisor-agent-[hash].us-central1.run.app`
- 🏗️ **Architecture**: `https://architecture-agent-[hash].us-central1.run.app`  
- ⚙️ **Management**: `https://gcp-management-agent-[hash].us-central1.run.app`

## 📁 Project Structure

```
gcp-cloudmate-ai/
├── 📱 app.py                          # Chainlit UI application
├── 📄 chainlit.md                     # UI configuration
├── 📋 requirements.txt                # UI dependencies
├── 🐳 Dockerfile.*                    # Docker configurations
├── ☁️ cloudbuild-*.yaml              # Cloud Build configs
├── 🚀 deploy_local.sh                # Local deployment script
├── ☁️ deploy_cloud.sh                # Cloud deployment script
├── 🛑 stop_local.sh                  # Stop local services
├── 📂 agents/
│   ├── 🎯 orchestrator_agent/
│   │   ├── agent.py                   # Agent logic
│   │   ├── session_task_manager.py   # Session management
│   │   ├── requirements.txt          # Agent-specific deps
│   │   └── __main__.py               # FastAPI server
│   ├── 💡 gcp_advisor_agent/
│   │   ├── agent.py
│   │   ├── tools.py                  # GCP advisory tools
│   │   ├── requirements.txt
│   │   └── __main__.py
│   ├── 🏗️ architecture_agent/
│   │   ├── agent.py
│   │   ├── requirements.txt
│   │   └── __main__.py
│   └── ⚙️ gcp_management_agent/
│       ├── agent.py
│       ├── tools.py                  # GCP resource tools
│       ├── requirements.txt
│       └── __main__.py
└── 📂 common/
    └── a2a_server.py                 # Shared server utilities
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI API key | Yes |
| `ORCHESTRATOR_URL` | Orchestrator service URL | Auto-set |
| `GCP_ADVISOR_URL` | GCP Advisor service URL | Auto-set |
| `ARCHITECTURE_URL` | Architecture service URL | Auto-set |
| `GCP_MANAGEMENT_URL` | Management service URL | Auto-set |

### Agent-Specific Configuration

Each agent has its own `requirements.txt` for lightweight Docker images:

- **Orchestrator**: Minimal dependencies for routing
- **GCP Advisor**: AI and GCP client libraries
- **Architecture**: AI libraries for diagram generation  
- **Management**: GCP Storage and Firestore clients

## 🧪 Usage Examples

### 1. Service Recommendations
```
User: "I need to build a real-time chat application for 10,000 users"

Response: Detailed recommendations for:
- Cloud Run for API services
- Cloud Firestore for real-time data
- Cloud Load Balancer for traffic distribution
- Cost estimates and scaling considerations
```

### 2. Architecture Design
```
User: "Design a data processing pipeline for IoT sensor data"

Response: Complete architecture including:
- Cloud IoT Core for device management
- Cloud Functions for data processing
- BigQuery for analytics
- Visual PlantUML diagram
```

### 3. Resource Management
```
User: "Create a Firestore database called 'user-profiles'"

Response: Creates database with optimal settings and provides configuration details
```

## 🐛 Troubleshooting

### Common Issues

**1. API Key Errors**
```bash
# Set your API key
export GOOGLE_API_KEY="your_key_here"
```

**2. Permission Errors**
```bash
# Make scripts executable
chmod +x deploy_local.sh deploy_cloud.sh stop_local.sh
```

**3. Port Conflicts**
```bash
# Check what's using ports
lsof -i :8001,:8002,:8003,:8004,:8080

# Stop conflicting processes
./stop_local.sh
```

**4. Cloud Deployment Issues**
```bash
# Check service status
gcloud run services list --region=us-central1 --project=YOUR_PROJECT_ID

# View logs
gcloud logs read --project=YOUR_PROJECT_ID
```

### Getting Help

- 📖 Check the [Google Cloud Documentation](https://cloud.google.com/docs)
- 🐛 [Open an Issue](https://github.com/yourusername/gcp-cloudmate-ai/issues)
- 💬 [Discussions](https://github.com/yourusername/gcp-cloudmate-ai/discussions)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone the repo
git clone git@github.com:Ngoga-Musagi/gcp-cloudmate-ai.git
# Install development dependencies  
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
black . && flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **Google Cloud Platform** for providing the infrastructure
- **Google AI (Gemini)** for powering the intelligent agents
- **Chainlit** for the beautiful chat interface
- **FastAPI** for the robust API framework
- **Google ADK** for agent development tools

## 🔮 Roadmap

- [ ] **Multi-cloud support** (AWS, Azure integration)
- [ ] **Cost optimization recommendations**
- [ ] **Security compliance scanning**
- [ ] **Infrastructure as Code generation**
- [ ] **Voice interface support**
- [ ] **Mobile application**

---

**Made with ❤️ by [Your Name]**

*Let your ideas meet the cloud—instantly, intelligently, and effortlessly.*

## 📊 Stats

[![GitHub stars](https://img.shields.io/github/stars/yourusername/gcp-cloudmate-ai?style=social)](https://github.com/yourusername/gcp-cloudmate-ai/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/gcp-cloudmate-ai?style=social)](https://github.com/yourusername/gcp-cloudmate-ai/network/members)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/gcp-cloudmate-ai)](https://github.com/yourusername/gcp-cloudmate-ai/issues)

---

*🚀 Ready to revolutionize your cloud experience? [Get started now](#-quick-start)!*