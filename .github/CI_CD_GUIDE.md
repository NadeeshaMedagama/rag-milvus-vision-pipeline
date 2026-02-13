# CI/CD Pipeline Documentation

This document describes the comprehensive CI/CD pipeline setup for the Python RAG with Milvus application.

## Overview

The project uses GitHub Actions for continuous integration, continuous deployment, security scanning, and automated dependency management.

## Workflow Files

### 1. CI/CD Pipeline (`ci.yml`)

**Trigger:** Push and PR to `main` and `develop` branches

**Jobs:**
- **lint-and-test**: Code quality and security checks
  - Black formatting check
  - isort import sorting
  - flake8 linting
  - pylint analysis
  - mypy type checking
  - Bandit security scanning
  - Safety vulnerability checks
  - pytest with coverage reporting
  - Codecov integration

- **docker-build-test**: Container validation
  - Docker image build
  - Container functionality test
  - Trivy vulnerability scanning
  - SARIF report upload to GitHub Security

- **build-status**: Overall status check

### 2. CodeQL Security Analysis (`codeql.yml`)

**Trigger:** Push, PR, weekly schedule (Mondays 6 AM UTC), manual

**Features:**
- Advanced static code analysis
- Python-specific security patterns
- Weekly automated scans
- Results published to Security tab
- Integrated with GitHub Advanced Security

### 3. Docker Build & Publish (`docker.yml`)

**Trigger:** Push to main, version tags, PR, manual

**Features:**
- Multi-platform builds (amd64, arm64)
- GitHub Container Registry publishing
- Semantic versioning
- Trivy vulnerability scanning
- SBOM generation
- Build cache optimization
- Automated tagging (latest, version, sha)

**Image Tags:**
- `latest` - Latest main branch build
- `v1.0.0` - Semantic version tags
- `main-abc1234` - Branch with commit SHA
- `v1.0` - Major.Minor version
- `v1` - Major version

### 4. Release Management (`release.yml`)

**Trigger:** Version tags (v*.*.*), manual dispatch

**Features:**
- Automated changelog generation
- GitHub Release creation
- Source distribution packaging
- Release notes with categorized changes
- Docker image publishing with version tags

**Release Categories:**
- 🚀 Features (feature, enhancement labels)
- 🐛 Bug Fixes (bug, fix labels)
- 📚 Documentation (documentation, docs labels)
- 🔒 Security (security label)
- 🧰 Maintenance (maintenance, chore, dependencies labels)

### 5. Dependency Updates Check (`dependency-check.yml`)

**Trigger:** Weekly schedule (Mondays 8 AM UTC), PR on dependency files, manual

**Features:**
- Outdated package detection
- pip-audit security scanning
- License compliance reporting
- Docker base image updates
- GitHub Actions version tracking

### 6. Dependabot Auto-Merge (`dependabot-auto-merge.yml`)

**Trigger:** Dependabot PRs

**Features:**
- Auto-approve minor and patch updates
- Auto-merge patch updates
- Automated PR comments

## Dependabot Configuration

**Update Schedule:** Weekly on Mondays at 6 AM UTC

**Ecosystems Monitored:**
- Python packages (pip)
- Docker base images
- GitHub Actions

**Grouping:**
- LangChain packages (langchain*, langgraph*)
- Azure packages (*azure*, *openai*)
- Flask packages (flask*)
- Security patches (all patch updates)

## Setup Instructions

### 1. Repository Settings

1. **Enable GitHub Actions:**
   - Go to repository Settings → Actions → General
   - Select "Allow all actions and reusable workflows"

2. **Workflow Permissions:**
   - Go to Settings → Actions → General → Workflow permissions
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

3. **GitHub Container Registry:**
   - Permissions are handled automatically via `GITHUB_TOKEN`
   - Images published to `ghcr.io/OWNER/REPO`

### 2. Enable Security Features

1. **Go to Settings → Security → Code security and analysis**

2. **Enable the following:**
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Dependabot version updates
   - ✅ Code scanning (CodeQL)
   - ✅ Secret scanning

### 3. Branch Protection Rules (Recommended)

**For `main` branch:**
- Require pull request reviews
- Require status checks to pass:
  - `lint-and-test`
  - `docker-build-test`
  - `CodeQL`
- Require branches to be up to date
- Do not allow force pushes
- Do not allow deletions

### 4. Configure Secrets (if needed)

Most workflows use `GITHUB_TOKEN` (automatically provided), but you can add custom secrets:

**Settings → Secrets and variables → Actions → New repository secret**

Common secrets:
- `CODECOV_TOKEN` - For Codecov integration (optional)
- Custom deployment credentials (if deploying to external services)

### 5. Update Badge URLs

Replace `YOUR_USERNAME` in README.md badges with your GitHub username/organization.

## Usage

### Running Workflows Manually

1. Go to **Actions** tab
2. Select the workflow
3. Click **Run workflow**
4. Select branch and provide inputs (if any)

### Creating a Release

```bash
# Create and push a version tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

This automatically triggers:
- Release workflow
- Docker image build with version tags
- GitHub Release creation
- Changelog generation

### Viewing Results

**Workflow Runs:**
- GitHub → Actions tab

**Security Findings:**
- GitHub → Security tab
- Code scanning alerts (CodeQL)
- Dependabot alerts
- Secret scanning alerts

**Docker Images:**
- GitHub → Packages
- Or: `https://github.com/users/USERNAME/packages/container/package/REPO`

**Coverage Reports:**
- Workflow artifacts (download from Actions)
- Codecov dashboard (if configured)

## Workflow Artifacts

Each workflow produces artifacts that are retained:

| Workflow | Artifact | Retention |
|----------|----------|-----------|
| CI/CD | Bandit security report | 30 days |
| CI/CD | Safety vulnerability report | 30 days |
| CI/CD | Coverage reports (XML, HTML) | 30 days |
| CI/CD | Trivy vulnerability report | 30 days |
| CodeQL | SARIF results | 30 days |
| Docker | SBOM (Software Bill of Materials) | 90 days |
| Dependency Check | Outdated packages report | 30 days |
| Dependency Check | Security audit report | 30 days |
| Dependency Check | License report | 90 days |

## Monitoring and Alerts

### Email Notifications

GitHub sends emails for:
- Failed workflow runs
- Security vulnerabilities (Dependabot)
- CodeQL findings
- Failed deployments

### Status Checks

Pull requests show status checks:
- ✅ CI/CD Pipeline passing
- ✅ CodeQL analysis complete
- ✅ Docker build successful

### Security Alerts

**Critical vulnerabilities** trigger:
- Dependabot security alerts
- CodeQL findings in Security tab
- Trivy scan results

## Best Practices

### 1. Commit Messages

Use conventional commits for better changelog:
```
feat: add new feature
fix: resolve bug
docs: update documentation
chore: dependency updates
security: fix vulnerability
```

### 2. Version Tags

Follow semantic versioning:
- `v1.0.0` - Major release (breaking changes)
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)

### 3. Pull Requests

- Create PRs from feature branches
- Wait for CI/CD to pass
- Review security scan results
- Merge using squash commits

### 4. Dependency Management

- Review Dependabot PRs weekly
- Auto-merge is enabled for patch updates
- Manually review minor/major updates
- Check for breaking changes

### 5. Security

- Never commit secrets to repository
- Use `.env` for local credentials
- Review security alerts promptly
- Keep dependencies up to date

## Troubleshooting

### Workflow Fails

1. Check workflow logs in Actions tab
2. Review error messages
3. Common issues:
   - Missing dependencies
   - Failed tests
   - Linting errors
   - Security vulnerabilities

### Docker Build Fails

1. Test build locally: `docker build -t test .`
2. Check Dockerfile syntax
3. Verify base image availability
4. Review layer caching

### Dependabot Issues

1. Check Dependabot logs in Security tab
2. Review compatibility issues
3. Manually update if auto-update fails

### CodeQL Warnings

1. Review findings in Security tab
2. Fix security issues
3. Mark false positives as "Won't fix" with justification

## Continuous Improvement

### Metrics to Monitor

- Build success rate
- Test coverage percentage
- Security vulnerabilities count
- Deployment frequency
- Time to fix issues

### Regular Reviews

- Monthly: Review security findings
- Quarterly: Update base images
- Annually: Review CI/CD pipeline efficiency

## Support

For issues or questions:
1. Check workflow logs
2. Review GitHub Actions documentation
3. Open an issue in the repository

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Semantic Versioning](https://semver.org/)

