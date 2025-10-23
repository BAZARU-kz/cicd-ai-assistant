# AI Assistant CI/CD Setup Guide

## Prerequisites

### 1. Infrastructure Setup
- 4 VMs in private network (10.200.0.0/24)
- Bastion server (10.200.0.5) with Jenkins, Vault, kubectl, Caddy
- Kubernetes cluster (10.200.0.11, 10.200.0.12)
- Database server (10.200.0.10) with PostgreSQL

### 2. Required Credentials in Jenkins
- `TOKEN`: Telegram bot token for notifications
- `CHAT_ID`: Telegram chat ID for notifications
- `kuber-host-token`: Kubernetes cluster access token
- AWS ECR access configured on Jenkins server

### 3. Vault Secrets Setup
Required Vault paths and secrets:
```
secret/data/ai-assistant/staging/backend/
secret/data/ai-assistant/staging/taskiq/
secret/data/ai-assistant/prod/backend/
secret/data/ai-assistant/prod/taskiq/
```

Required Kubernetes secrets:
- `staging-backend-vault-token`
- `staging-taskiq-vault-token`
- `prod-backend-vault-token`
- `prod-taskiq-vault-token`
- `vault-url`

## Installation Steps

### Step 1: Setup Ingress Controller
```bash
# Apply NGINX Ingress Controller
kubectl apply -f ingress/nginx-ingress-controller.yaml

# Apply Cert-Manager for SSL
kubectl apply -f ingress/cert-manager.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=ingress-nginx \
  --timeout=90s
```

### Step 2: Create Namespaces
```bash
# Create staging namespace
kubectl apply -f kubernetes/staging/namespace.yaml

# Create production namespace
kubectl apply -f kubernetes/prod/namespace.yaml
```

### Step 3: Setup Database
On database server (10.200.0.10):
```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE "ai-assistant-staging";
CREATE DATABASE "ai-assistant-prod";

-- Create user (if needed)
CREATE USER aiassistant WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE "ai-assistant-staging" TO aiassistant;
GRANT ALL PRIVILEGES ON DATABASE "ai-assistant-prod" TO aiassistant;
```

### Step 4: Configure Vault Secrets
Example environment variables needed in Vault:

**Backend secrets** (`secret/data/ai-assistant/{environment}/backend/`):
```
DB_URI=postgresql://aiassistant:password@10.200.0.10:5432/ai-assistant-{environment}
REDIS_URL=ai-assistant-service-redis-{environment}
RABBITMQ_HOST=ai-assistant-service-rabbitmq-{environment}
RABBITMQ_PORT=5672
RABBITMQ_USER=aiassistant
RABBITMQ_PASSWORD=aiassistant
RABBITMQ_VHOST=/
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=https://ai-assistant-{environment}.zymran.com
```

**Taskiq secrets** (`secret/data/ai-assistant/{environment}/taskiq/`):
```
DB_URI=postgresql://aiassistant:password@10.200.0.10:5432/ai-assistant-{environment}
REDIS_URL=ai-assistant-service-redis-{environment}
RABBITMQ_HOST=ai-assistant-service-rabbitmq-{environment}
RABBITMQ_PORT=5672
RABBITMQ_USER=aiassistant
RABBITMQ_PASSWORD=aiassistant
RABBITMQ_VHOST=/
```

### Step 5: Create Kubernetes Secrets
```bash
# Create Vault token secrets for staging
kubectl create secret generic staging-backend-vault-token \
  --from-literal=staging-backend-vault-token="your_vault_token" \
  -n ai-assistant-staging

kubectl create secret generic staging-taskiq-vault-token \
  --from-literal=staging-taskiq-vault-token="your_vault_token" \
  -n ai-assistant-staging

# Create Vault URL secret
kubectl create secret generic vault-url \
  --from-literal=vault-url="https://your-vault-url:8200" \
  -n ai-assistant-staging

# Repeat for production namespace
kubectl create secret generic prod-backend-vault-token \
  --from-literal=prod-backend-vault-token="your_vault_token" \
  -n ai-assistant-prod

kubectl create secret generic prod-taskiq-vault-token \
  --from-literal=prod-taskiq-vault-token="your_vault_token" \
  -n ai-assistant-prod

kubectl create secret generic vault-url \
  --from-literal=vault-url="https://your-vault-url:8200" \
  -n ai-assistant-prod
```

### Step 6: Setup Jenkins Jobs
1. Create new Pipeline job in Jenkins
2. Configure Git repository: `https://github.com/your-org/cicd-ai-assistant`
3. Set Pipeline script path:
   - Staging: `jenkins/Jenkinsfile.staging`
   - Production: `jenkins/Jenkinsfile.prod`
4. Configure build triggers (manual for now)

### Step 7: DNS Configuration
Point your domains to the ingress controller's external IP:
```
ai-assistant-staging.zymran.com -> <ingress-external-ip>
ai-assistant-prod.zymran.com -> <ingress-external-ip>
```

### Step 8: Deploy Infrastructure Services
```bash
# Deploy Redis and RabbitMQ for staging
kubectl apply -f kubernetes/staging/redis-rabbitmq.yaml

# Deploy Redis and RabbitMQ for production
kubectl apply -f kubernetes/prod/redis-rabbitmq.yaml
```

## Testing the Pipeline

### 1. Initial Deployment
- Trigger the Jenkins job manually
- Check Telegram notifications
- Verify services are running: `kubectl get pods -n ai-assistant-staging`

### 2. Migration Testing
- Make a commit with message "DO_MIGRATIONS"
- Trigger pipeline
- Verify migration notification in Telegram

### 3. Access Applications
- Staging: https://ai-assistant-staging.zymran.com
- Production: https://ai-assistant-prod.zymran.com
- API Docs: https://ai-assistant-staging.zymran.com/docs

## Troubleshooting

### Common Issues
1. **ECR Authentication**: Ensure AWS credentials are configured on Jenkins server
2. **Vault Connection**: Check Vault tokens and network connectivity
3. **Database Connection**: Verify database credentials and network access
4. **Ingress Issues**: Check ingress controller logs and DNS configuration

### Useful Commands
```bash
# Check pod logs
kubectl logs -f deployment/ai-assistant-deploy-backend-staging -n ai-assistant-staging

# Check ingress status
kubectl get ingress -n ai-assistant-staging

# Check secrets
kubectl get secrets -n ai-assistant-staging

# Port forward for debugging
kubectl port-forward svc/ai-assistant-service-backend-staging 8000:8000 -n ai-assistant-staging
```