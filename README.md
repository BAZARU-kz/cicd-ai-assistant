# AI Assistant CI/CD Pipeline

This repository contains the CI/CD pipeline configuration for deploying the AI Assistant application to Kubernetes.

## Infrastructure Overview

- **Bastion Server** (10.200.0.5): Jenkins, Vault, kubectl, Caddy
- **Kubernetes Nodes**: 10.200.0.11, 10.200.0.12
- **Database Server** (10.200.0.10): PostgreSQL
- **Container Registry**: AWS ECR `863128715353.dkr.ecr.eu-central-1.amazonaws.com`

## Environments

### Staging
- **Namespace**: `ai-assistant-staging`
- **Domain**: `ai-assistant-staging.zymran.com`
- **Database**: `ai-assistant-staging` on 10.200.0.10

### Production
- **Namespace**: `ai-assistant-prod`
- **Domain**: `ai-assistant-prod.zymran.com`
- **Database**: `ai-assistant-prod` on 10.200.0.10

## Repository Structure

```
cicd-ai-assistant/
├── jenkins/                    # Jenkins pipeline files
│   ├── Jenkinsfile.staging    # Staging deployment pipeline
│   └── Jenkinsfile.prod       # Production deployment pipeline
├── kubernetes/                 # Kubernetes manifests
│   ├── staging/               # Staging environment
│   └── prod/                  # Production environment
├── docker/                    # Docker configurations
│   ├── Dockerfile.backend.staging
│   ├── Dockerfile.backend.prod
│   ├── Dockerfile.frontend.staging
│   └── Dockerfile.frontend.prod
├── scripts/                   # Utility scripts
│   ├── load_env.py           # Vault integration script
│   ├── start-staging.sh      # Backend startup script (staging)
│   └── start-prod.sh         # Backend startup script (production)
└── ingress/                  # Ingress controller setup
```

## Services Deployed

1. **Dashboard Backend** (FastAPI, port 8000)
2. **Dashboard Frontend** (React/Vite static, port 3000)
3. **Background Workers** (Taskiq workers)
4. **Redis** (Cache and session storage)
5. **RabbitMQ** (Message queue)

## Pipeline Features

- Git metadata extraction (committer, hash, message)
- Telegram notifications (start, success, failure)
- Multi-stage Docker builds with ECR push
- Vault integration for secrets management
- Database migrations triggered by "DO_MIGRATIONS" commit message
- Dynamic Kubernetes manifest updates
- Docker cleanup post-deployment

## Setup Instructions

### 1. Vault Configuration
Ensure the following secrets exist in Vault:
- Path: `secret/data/ai-assistant/{environment}/{application}/`
- Required tokens: `staging-backend-vault-token`, `vault-url`

### 2. Jenkins Setup
- Import the Jenkinsfile for your target environment
- Configure credentials: Telegram token, chat ID, AWS ECR access
- Set up kubectl credentials for the Kubernetes cluster

### 3. Kubernetes Setup
- Apply ingress controller configuration
- Create namespaces: `ai-assistant-staging`, `ai-assistant-prod`
- Configure DNS for domains

## Manual Deployment Trigger

Deployments are triggered manually through Jenkins UI. The pipeline will:
1. Extract git metadata and send start notification
2. Build backend and frontend Docker images
3. Push images to ECR with build number and latest tags
4. Update Kubernetes manifests with new image tags
5. Check for migration trigger in commit message
6. Deploy to Kubernetes cluster
7. Clean up Docker images and send completion notification