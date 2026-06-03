# FoodOps Runbook — Common Issues and How to Fix Them

A runbook is a document that lists common problems and their solutions.
DevOps engineers use this during incidents to fix issues quickly.

---

## Issue 1 — Pod is stuck in CrashLoopBackOff

**What it means:**
The pod keeps crashing and restarting in a loop. Kubernetes is trying to restart it but it keeps failing.

**How to detect:**
```bash
kubectl get pods -n foodops-prod
# You will see: STATUS = CrashLoopBackOff
```

**How to fix:**
```bash
# Step 1 — check the logs to see why it crashed
kubectl logs <pod-name> -n foodops-prod

# Step 2 — describe the pod for more details
kubectl describe pod <pod-name> -n foodops-prod

# Step 3 — if it's a code bug, fix the code and redeploy
# Step 4 — if it's a config issue, check environment variables
kubectl get pod <pod-name> -n foodops-prod -o yaml
```

---

## Issue 2 — ImagePullBackOff

**What it means:**
Kubernetes cannot pull the Docker image from ACR. The pod cannot start.

**How to detect:**
```bash
kubectl get pods -n foodops-prod
# You will see: STATUS = ImagePullBackOff
```

**Common causes:**
- Wrong image name or tag
- AKS does not have permission to pull from ACR
- ACR is down

**How to fix:**
```bash
# Step 1 — check the exact error
kubectl describe pod <pod-name> -n foodops-prod

# Step 2 — verify the image exists in ACR
az acr repository show-tags --name foodopsacr --repository menu-service

# Step 3 — verify AKS has AcrPull permission
az role assignment list --scope <acr-resource-id>

# Step 4 — if permission is missing, re-run terraform apply
terraform apply
```

---

## Issue 3 — Pod is Pending (not starting)

**What it means:**
The pod is waiting to be scheduled on a node. It hasn't started yet.

**How to detect:**
```bash
kubectl get pods -n foodops-prod
# You will see: STATUS = Pending
```

**Common causes:**
- Not enough CPU or memory on the nodes
- Node is full

**How to fix:**
```bash
# Step 1 — check why it's pending
kubectl describe pod <pod-name> -n foodops-prod
# Look for "Insufficient cpu" or "Insufficient memory"

# Step 2 — check node resources
kubectl top nodes

# Step 3 — if nodes are full, scale up the node pool
az aks scale \
  --resource-group foodops-rg \
  --name foodops-aks \
  --node-count 3
```

---

## Issue 4 — Deployment is stuck, pods not updating

**What it means:**
You deployed a new version but the old pods are still running. New pods won't start.

**How to detect:**
```bash
kubectl rollout status deployment/menu-service -n foodops-prod
# You will see it hanging
```

**How to fix:**
```bash
# Step 1 — check what's wrong
kubectl describe deployment menu-service -n foodops-prod

# Step 2 — if the new image is bad, rollback to previous version
kubectl rollout undo deployment/menu-service -n foodops-prod

# Step 3 — verify rollback worked
kubectl rollout status deployment/menu-service -n foodops-prod
kubectl get pods -n foodops-prod
```

---

## Issue 5 — Service not accessible from outside

**What it means:**
The app is running but users cannot reach it from the internet.

**How to detect:**
```bash
kubectl get services -n foodops-prod
# External IP shows <pending> for too long
```

**How to fix:**
```bash
# Step 1 — check service status
kubectl describe service order-service -n foodops-prod

# Step 2 — wait a few minutes, Azure LoadBalancer takes time to provision
# Step 3 — if still pending after 5 minutes, delete and recreate the service
kubectl delete service order-service -n foodops-prod
helm upgrade foodops-prod ./helm/foodops --namespace foodops-prod

# Step 4 — check Azure Load Balancer in the portal
```

---

## Issue 6 — Pipeline failing at build stage

**What it means:**
GitHub Actions cannot build the Docker image or push to ACR.

**Common causes:**
- Wrong ACR credentials in GitHub Secrets
- ACR name is wrong
- Docker build error in the code

**How to fix:**
```bash
# Step 1 — check the pipeline logs in GitHub Actions tab

# Step 2 — verify secrets are correct in GitHub
# Go to repo Settings → Secrets → check ACR_USERNAME and ACR_PASSWORD

# Step 3 — test locally first
docker build -t menu-service ./menu-service
docker login foodopsacr.azurecr.io
docker push foodopsacr.azurecr.io/menu-service:test
```

---

## Issue 7 — Order Service cannot reach Menu Service

**What it means:**
Orders are failing because Order Service cannot communicate with Menu Service inside the cluster.

**How to detect:**
```bash
# Place an order and get error: "Menu Service unavailable"
# Or check logs
kubectl logs <order-service-pod> -n foodops-prod
```

**How to fix:**
```bash
# Step 1 — check if Menu Service pod is running
kubectl get pods -n foodops-prod

# Step 2 — check if Menu Service has a ClusterIP service
kubectl get services -n foodops-prod

# Step 3 — test connection from inside the cluster
kubectl exec -it <order-service-pod> -n foodops-prod -- curl http://menu-service:8000/health

# Step 4 — if service is missing, redeploy with Helm
helm upgrade foodops-prod ./helm/foodops --namespace foodops-prod
```

---

## Quick Reference Commands

```bash
# Check all pods in an environment
kubectl get pods -n foodops-dev
kubectl get pods -n foodops-staging
kubectl get pods -n foodops-prod

# Check logs
kubectl logs <pod-name> -n foodops-prod
kubectl logs <pod-name> -n foodops-prod --previous  # logs from crashed pod

# Restart a deployment
kubectl rollout restart deployment/menu-service -n foodops-prod

# Rollback to previous version
kubectl rollout undo deployment/menu-service -n foodops-prod

# Check resource usage
kubectl top pods -n foodops-prod
kubectl top nodes

# Get public IP of Order Service
kubectl get service order-service -n foodops-prod
```
