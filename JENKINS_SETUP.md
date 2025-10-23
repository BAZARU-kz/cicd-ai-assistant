# Jenkins Multi-Repository Setup Guide

## Problem
Jenkins error: `lstat cicd-ai-assistant: no such file or directory`

This happens because Jenkins is only checking out the `ai-assistant` repository but the pipeline tries to access files from `cicd-ai-assistant` repository.

## Solution Options

### Option 1: Multiple SCM Plugin (Recommended)

1. **Install Plugin**: Install "Multiple SCMs" plugin in Jenkins
2. **Job Configuration**:
   - Go to your Jenkins job configuration
   - In "Source Code Management" section:
     - Select "Multiple SCMs"
     - Add SCM #1: Git
       - Repository URL: `https://github.com/your-org/ai-assistant.git`
       - Branch: `main`
       - Additional Behaviours: Check out to sub-directory: `ai-assistant`
     - Add SCM #2: Git  
       - Repository URL: `https://github.com/your-org/cicd-ai-assistant.git`
       - Branch: `main`
       - Additional Behaviours: Check out to sub-directory: `cicd-ai-assistant`

3. **Pipeline Script Path**: `cicd-ai-assistant/jenkins/Jenkinsfile.staging`

### Option 2: Pipeline with Checkout Steps

Replace the current Jenkinsfile with this approach:

```groovy
pipeline {
    agent any
    
    environment {
        CONTAINER_REPO_URI = "863128715353.dkr.ecr.eu-central-1.amazonaws.com"
    }
    
    stages {
        stage('Checkout Repositories') {
            steps {
                // Checkout ai-assistant repository
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://github.com/your-org/ai-assistant.git']],
                    extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'ai-assistant']]
                ])
                
                // Checkout cicd-ai-assistant repository
                checkout([
                    $class: 'GitSCM', 
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://github.com/your-org/cicd-ai-assistant.git']],
                    extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'cicd-ai-assistant']]
                ])
            }
        }
        
        stage('create-tags') {
            steps {
                script {
                    FAILED_STAGE = "${STAGE_NAME}"
                    
                    // Extract git metadata from ai-assistant repo
                    dir('ai-assistant') {
                        COMMITTER_EMAIL = sh(returnStdout: true, script: 'git log --format="%ae" | head -1').trim()
                        COMMITTER_USER = sh(returnStdout: true, script: 'git log --format="%an" | head -1').trim()
                        GIT_HASH = sh(returnStdout: true, script: 'echo "${GIT_COMMIT: -6}" | head -1').trim()
                        COMMIT_MESSAGE = sh(returnStdout: true, script: 'git log --format=%B -n 1 "${GIT_COMMIT}"').trim()
                    }
                    
                    echo "Committer: ${COMMITTER_USER} (${COMMITTER_EMAIL})"
                    echo "Commit Hash: ${GIT_HASH}"
                    echo "Commit Message: ${COMMIT_MESSAGE}"
                    echo "Container Repo: ${CONTAINER_REPO_URI}"
                }
                
                // Send start notification
                withCredentials([
                    string(credentialsId: 'TOKEN', variable: 'TOKEN'), 
                    string(credentialsId: 'CHAT_ID', variable: 'CHAT_ID')
                ]) {
                    sh """
                        curl -iX GET https://api.telegram.org/bot\$TOKEN/sendMessage \
                        -d chat_id=\$CHAT_ID \
                        -d text="Pipeline: \$JOB_BASE_NAME 🚀STARTED\\nBuild url: \$BUILD_URL\\n✉️Message: \$COMMIT_MESSAGE\\nUser/email: \$COMMITTER_USER/\$COMMITTER_EMAIL\\nID: \$GIT_HASH"
                    """
                }
            }
        }
        
        // Rest of your stages...
    }
}
```

### Option 3: Copy Files Approach (Simplest)

1. **Copy CI/CD files to ai-assistant repository**:
   ```bash
   # In your ai-assistant repository
   mkdir -p docker scripts
   cp ../cicd-ai-assistant/docker/* docker/
   cp ../cicd-ai-assistant/scripts/* scripts/
   ```

2. **Update Jenkinsfile paths**:
   - Change `cicd-ai-assistant/docker/Dockerfile.backend.staging` to `docker/Dockerfile.backend.staging`
   - Change `cicd-ai-assistant/scripts/` to `scripts/`
   - Change `cicd-ai-assistant/kubernetes/` to `kubernetes/`

3. **Use single repository** in Jenkins pointing to `ai-assistant`

## Quick Fix for Current Setup

If you want to quickly fix the current Jenkins job:

### Update Jenkins Job Configuration:
1. Go to Jenkins job configuration
2. In "Source Code Management":
   - Change from single Git repository to "Multiple SCMs"
   - Add both repositories as described in Option 1

### Or Update the Build Commands:
Change the Docker build commands in Jenkins to use relative paths from the workspace root:

```bash
# Current (failing):
docker build -f cicd-ai-assistant/docker/Dockerfile.backend.staging

# Should be (if using Option 1):
docker build -f cicd-ai-assistant/docker/Dockerfile.backend.staging

# Or (if using Option 3):
docker build -f docker/Dockerfile.backend.staging
```

## Recommended Solution

**Use Option 1 (Multiple SCM Plugin)** because it:
- Keeps repositories separate
- Maintains clean separation of concerns  
- Works with existing Jenkinsfile structure
- Allows independent versioning of CI/CD configs

The key is ensuring Jenkins workspace has this structure:
```
jenkins-workspace/
├── ai-assistant/
└── cicd-ai-assistant/
```