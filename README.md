# Zero-Touch Deployment Pipeline
### Terraform · GitHub Actions · AWS ECS Fargate

> Fully automated CI/CD pipeline that deploys a Python Flask 
> application from commit to production in under 10 minutes, 
> with automatic rollback on health check failure.

---

## What This Project Demonstrates
- Infrastructure as Code with modularized Terraform
- Multi-environment promotion pipeline (staging → production)
- Zero-downtime rolling deployments on ECS Fargate
- Automatic rollback via ECS Deployment Circuit Breaker
- Manual approval gate protecting production

---

## Architecture

Internet → ALB (public subnet) → ECS Fargate Tasks (private subnet)
                                        ↑
                                   ECR (Docker images)
                                        ↑
                              GitHub Actions Pipeline

---

## Pipeline Flow
ci-build → terraform-lint → deploy-staging → [approval] → deploy-production
   ↓              ↓               ↓                              ↓
Build image   Validate TF    Auto deploy               Manual approval
Push to ECR   formatting     Force refresh             required before
SHA tagged    and syntax      + smoke test              production runs

---

## Project Structure

```text
.
├── app
│   ├── app.py
│   ├── Dockerfile
│   ├── index.js
│   └── requirements.txt
├── README.md
└── terraform
    ├── environments
    │   ├── dev
    │   │   ├── backend.tf
    │   │   ├── main.tf
    │   │   └── provider.tf
    │   ├── production
    │   │   ├── backend.tf
    │   │   ├── main.tf
    │   │   └── provider.tf
    │   └── staging
    │       ├── backend.tf
    │       ├── main.tf
    │       └── provider.tf
    ├── global
    │   ├── bootstrap
    │   └── ecr
    │       ├── backend.tf
    │       ├── main.tf
    │       └── provider.tf
    └── modules
        ├── alb
        │   ├── main.tf
        │   ├── outputs.tf
        │   └── variables.tf
        ├── compute
        │   ├── main.tf
        │   ├── outputs.tf
        │   └── variables.tf
        ├── monitoring
        │   ├── main.tf
        │   ├── outputs.tf
        │   └── variables.tf
        ├── networking
        │   ├── main.tf
        │   ├── outputs.tf
        │   └── variables.tf
        └── security
            ├── main.tf
            ├── outputs.tf
            └── variables.tf

15 directories, 32 files
```
---

## Terraform Modules
| Module     | What it creates                              |
|------------|----------------------------------------------|
| networking | VPC, subnets, IGW, NAT Gateway, route tables |
| security   | IAM roles, security groups                   |
| alb        | Application Load Balancer, target groups     |
| compute    | ECS cluster, task definition, service        |
| monitoring | CloudWatch log groups, alarms                |

---

## Prerequisites
- AWS Account with CLI configured
- Terraform installed
- Docker installed
- GitHub account

---

## Setup Instructions

### 1. Bootstrap (one time only)
[S3 + DynamoDB commands]

### 2. Configure GitHub Secrets
Add these in GitHub → Settings → Secrets → Actions:
| Secret | Value |
|--------|-------|
| AWS_ACCESS_KEY_ID | Your IAM key |
| AWS_SECRET_ACCESS_KEY | Your IAM secret |
| AWS_REGION | ap-south-1 |
| ECR_REPOSITORY | your ECR repo name |
| STAGING_ALB_URL | staging ALB DNS |

### 3. Deploy
git push origin main
# Pipeline auto-deploys to staging
# Approve the production gate in GitHub Actions

---

## Rollback Mechanism
ECS Deployment Circuit Breaker is enabled on all services.
If a new deployment fails health checks, ECS automatically 
reverts to the previous task definition. No manual intervention required.
Tested by intentionally breaking the /health endpoint.

---

## Runbook — Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
| ECS tasks restarting | Health check failing | Check CloudWatch: /ecs/app-staging |
| Pipeline blocked | Terraform state locked | Delete DynamoDB lock item |
| Deployment not updating | force-new-deployment missing | Check deploy.yml |

---

## Estimated Monthly Cost
| Resource | Cost |
|----------|------|
| ECS Fargate (2 tasks) | ~$15 |
| ALB (x2 environments) | ~$40 |
| NAT Gateway | ~$35 |
| ECR + CloudWatch | ~$5 |
| Total | ~$95/month |

---

Built by Pravin Bhatuse
