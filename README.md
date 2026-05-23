#  FoodOps — Cloud Native Food Ordering System

A production-grade DevOps project demonstrating microservices, Kubernetes, CI/CD, and Infrastructure as Code on Azure.

## Architecture

```
GitHub → GitHub Actions CI/CD → Azure Container Registry → AKS Cluster
                                                              ├── menu-service (2 pods)
                                                              └── order-service (2 pods)
                                                                    ↕ calls menu-service internally
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| App | Python FastAPI |
| Containers | Docker |
| Orchestration | Azure Kubernetes Service (AKS) |
| Image Registry | Azure Container Registry (ACR) |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |
| Packaging | Helm |
| Monitoring | Azure Monitor + Container Insights |

## Services

### Menu Service (port 8000)
- `GET /menu` — full menu
- `GET /menu/{category}` — filtered by category
- `GET /item/{id}` — single item (called internally by Order Service)
- `GET /health` — liveness probe

### Order Service (port 8001 / public port 80)
- `POST /order` — place an order (validates items with Menu Service)
- `GET /order/{id}` — get order status
- `GET /orders` — all orders
- `PATCH /order/{id}/status` — update status
- `GET /health` — liveness probe

## Getting Started

### 1. Provision Infrastructure with Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 2. Deploy to AKS with Helm
```bash
helm upgrade --install foodops ./helm/foodops \
  --set registry=<your-acr>.azurecr.io \
  --set imageTag=latest
```

### 3. Run Tests Locally
```bash
# Menu Service
cd menu-service && pip install -r requirements.txt && pytest tests/ -v

# Order Service
cd order-service && pip install -r requirements.txt && pytest tests/ -v
```

## CI/CD Pipeline

Every push to `main` triggers:
1. **Test** — pytest runs on both services
2. **Build** — Docker images built and pushed to ACR (tagged with commit SHA)
3. **Deploy** — Helm deploys both services to AKS

## Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `ACR_USERNAME` | Azure Container Registry username |
| `ACR_PASSWORD` | Azure Container Registry password |
| `AZURE_CREDENTIALS` | Azure service principal JSON |
