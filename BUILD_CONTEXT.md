# Build Context Instructions

## Important: Repository Setup

The Jenkins pipeline must be configured to build from the **ai-assistant** repository, not the cicd-ai-assistant repository.

## Setup Steps

### 1. Repository Structure
You should have both repositories in the same parent directory:
```
parent-directory/
├── ai-assistant/                    # Main application repository
│   ├── dashboard-backend/
│   ├── dashboard-frontend/
│   └── docker-compose.yml
└── cicd-ai-assistant/              # CI/CD configuration repository
    ├── jenkins/
    ├── kubernetes/
    ├── docker/
    └── scripts/
```

### 2. Jenkins Job Configuration

#### Option A: Multi-Repository Setup (Recommended)
1. **Primary Repository**: Set to `ai-assistant` repository
2. **Additional Repository**: Add `cicd-ai-assistant` as additional SCM
3. **Build Context**: Jenkins will build from `ai-assistant` root directory
4. **Pipeline Script Path**: `../cicd-ai-assistant/jenkins/Jenkinsfile.staging`

#### Option B: Single Repository with Submodules
1. Add `cicd-ai-assistant` as a git submodule in `ai-assistant`
2. Set Jenkins to use `ai-assistant` repository
3. Pipeline script path: `cicd-ai-assistant/jenkins/Jenkinsfile.staging`

#### Option C: Copy Dockerfiles to ai-assistant
1. Copy the Dockerfiles from `cicd-ai-assistant/docker/` to `ai-assistant/docker/`
2. Copy the scripts from `cicd-ai-assistant/scripts/` to `ai-assistant/scripts/`
3. Set Jenkins to use `ai-assistant` repository
4. Update Dockerfile paths in Jenkinsfile

### 3. Docker Build Context

The Docker builds expect this file structure from the build context root:
```
ai-assistant/                        # <- Build context root
├── dashboard-backend/app/
│   ├── pyproject.toml
│   ├── poetry.lock
│   ├── main.py
│   ├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── migrations/
│   └── tests/
├── dashboard-frontend/
│   ├── package.json
│   ├── src/
│   ├── nginx.conf
│   └── dist/ (created during build)
└── cicd-ai-assistant/              # <- Either submodule or copied files
    ├── docker/
    │   ├── Dockerfile.backend.staging
    │   ├── Dockerfile.backend.prod
    │   ├── Dockerfile.frontend.staging
    │   └── Dockerfile.frontend.prod
    └── scripts/
        ├── load_env.py
        ├── start-staging.sh
        └── start-prod.sh
```

### 4. Jenkins Pipeline Commands

The pipeline will run these Docker build commands from the `ai-assistant` directory:
```bash
# Backend staging build
docker build -f cicd-ai-assistant/docker/Dockerfile.backend.staging \
  -t ${CONTAINER_REPO_URI}/ai-assistant-backend-staging:${BUILD_NUMBER} .

# Frontend staging build  
docker build -f cicd-ai-assistant/docker/Dockerfile.frontend.staging \
  -t ${CONTAINER_REPO_URI}/ai-assistant-frontend-staging:${BUILD_NUMBER} .
```

## Recommended Approach

**Use Option A (Multi-Repository Setup)** for the cleanest separation of concerns:

1. Keep application code in `ai-assistant` repository
2. Keep CI/CD configurations in `cicd-ai-assistant` repository  
3. Configure Jenkins to checkout both repositories
4. Build from `ai-assistant` root with Dockerfiles from `cicd-ai-assistant`

This approach maintains separation while allowing the build context to access all necessary files.