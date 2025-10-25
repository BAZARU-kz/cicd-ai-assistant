# ⚠️ DEPRECATED: AI Assistant CI/CD Pipeline

## 🚨 This Repository is No Longer Used

**The CI/CD configuration has been moved to the main application repository.**

### ✅ New Location
All CI/CD configurations are now located in:
- **Repository**: `ai-assistant`
- **Branch**: `dara-cicd`
- **Path**: `config/`

### 📁 New Structure
```
ai-assistant/config/
├── jenkins/                    # Jenkins pipeline files
├── staging/                   # Staging environment configs
│   ├── docker/               # Dockerfiles
│   ├── kubernetes/           # K8s manifests
│   └── scripts/              # Startup scripts
└── prod/                     # Production environment configs
    ├── docker/               # Dockerfiles
    ├── kubernetes/           # K8s manifests
    └── scripts/              # Startup scripts
```

### 🔄 Migration Complete
- ✅ All configurations moved to `ai-assistant/dara-cicd` branch
- ✅ Simplified single-repository approach
- ✅ No multi-repository complexity
- ✅ Clean file paths and build context

### 🚀 How to Use
1. **Jenkins Setup**: Point to `ai-assistant` repository, `dara-cicd` branch
2. **Pipeline Script**: `config/jenkins/Jenkinsfile.staging` or `config/jenkins/Jenkinsfile.prod`
3. **Build Context**: Repository root (simple paths)

### 📖 Documentation
See the complete setup guide in the new location:
- `ai-assistant/config/README.md`

---

**This repository is kept for historical reference only.**