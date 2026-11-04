# MicroTask — Minikube Local Deployment Guide

All commands are PowerShell 5.1 on Windows 11.
Run PowerShell as a normal user (no admin required for these commands).

---

## Prerequisites check

```powershell
# Check Minikube
minikube version

# Check kubectl
kubectl version --client

# Check Helm (use full path until you restart your terminal)
C:\Users\it\helm-extract\windows-amd64\helm.exe version
# After restarting terminal, just use:
helm version

# Check Docker Desktop is running
docker version
```

---

## Step 1 — Start Minikube

```powershell
# Start Minikube with enough resources for all 4 services
minikube start --cpus=4 --memory=4096 --driver=docker

# Verify Minikube is running
minikube status
```

Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

## Step 2 — Load Docker images into Minikube

The images exist locally in Docker Desktop but Minikube runs its own Docker daemon.
We must load each image into Minikube's image cache.

```powershell
# Load all three application images
minikube image load microtask-api:latest
minikube image load microtask-worker:latest
minikube image load microtask-frontend:latest

# MySQL is pulled from Docker Hub automatically (imagePullPolicy: IfNotPresent)
# but you can pre-load it to avoid the pull:
minikube image load mysql:8.0

# Verify images are loaded
minikube image ls | Select-String "microtask"
```

---

## Step 3 — Install the Helm chart

```powershell
# Navigate to the repository root
cd E:\Shreik\microservices-eks-gitops-capstone

# Install with dev values (Minikube-specific settings)
helm install microtask helm/microtask -f helm/microtask/values-dev.yaml -n microtask --create-namespace

# You should see:
# NAME: microtask
# STATUS: deployed
# REVISION: 1
```

---

## Step 4 — Watch everything come up

```powershell
# Watch all Pods in the microtask namespace
kubectl get pods -n microtask -w

# In a separate terminal, watch all resources
kubectl get all -n microtask
```

Expected startup order:
1. `mysql-0` starts and becomes Ready (~30-60s)
2. `microtask-migrate` Job runs and completes
3. `api` Pod starts (initContainer waits for MySQL, then API starts)
4. `worker` Pod starts
5. `frontend` Pod starts

---

## Step 5 — Check all resources

```powershell
# All Pods
kubectl get pods -n microtask

# All Services
kubectl get svc -n microtask

# PersistentVolumeClaim (MySQL storage)
kubectl get pvc -n microtask

# StatefulSet (MySQL)
kubectl get statefulset -n microtask

# Deployments
kubectl get deployments -n microtask

# Migration Job status
kubectl get jobs -n microtask
```

All Pods should show `Running` and `1/1 READY`.
The migrate Job should show `1/1 COMPLETE`.

---

## Step 6 — Check migration Job logs

```powershell
# Get the migration Pod name
kubectl get pods -n microtask -l app.kubernetes.io/name=migrate

# View migration logs (replace <pod-name> with actual name)
kubectl logs -n microtask job/microtask-migrate
```

Expected output:
```
Waiting for MySQL to accept connections...
Running Alembic migrations...
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial
Migrations complete.
```

---

## Step 7 — Access the application

### Option A — kubectl port-forward (recommended for local dev)

Open three separate PowerShell terminals:

```powershell
# Terminal 1 — Frontend (access at http://localhost:3000)
kubectl port-forward svc/frontend 3000:80 -n microtask

# Terminal 2 — API direct access (http://localhost:8000/docs)
kubectl port-forward svc/api 8000:8000 -n microtask
```

Then open in browser:
- **Frontend dashboard**: http://localhost:3000
- **API Swagger docs**: http://localhost:8000/docs
- **API health**: http://localhost:8000/health
- **Prometheus metrics**: http://localhost:8000/metrics

### Option B — Minikube service URL

```powershell
# Get the Minikube IP
minikube ip

# Open frontend via NodePort (port 30080)
minikube service frontend -n microtask

# Or construct the URL manually:
# http://<minikube-ip>:30080
```

---

## Step 8 — Test the API health

```powershell
# With port-forward active on 8000:
curl http://localhost:8000/health
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

Expected response from /health:
```json
{"status": "healthy", "database": "connected", "version": "1.0.0"}
```

---

## Step 9 — Create and process a task

```powershell
# Create a task
curl -X POST http://localhost:8000/api/v1/tasks `
  -H "Content-Type: application/json" `
  -d '{"title":"Kubernetes Test Task","description":"Testing from Minikube","task_type":"DATA_PROCESSING","priority":"HIGH"}'

# List all tasks
curl http://localhost:8000/api/v1/tasks

# Check stats
curl http://localhost:8000/api/v1/stats
```

Wait 5-10 seconds and check again — the worker will pick up the PENDING task and process it.

---

## Step 10 — View logs

```powershell
# API logs
kubectl logs -n microtask deployment/api -f

# Worker logs (shows task processing)
kubectl logs -n microtask deployment/worker -f

# Frontend logs (Nginx access log)
kubectl logs -n microtask deployment/frontend -f

# MySQL logs
kubectl logs -n microtask statefulset/mysql -f

# Migration Job logs
kubectl logs -n microtask job/microtask-migrate
```

---

## Step 11 — Check MySQL data persistence

```powershell
# Connect to MySQL inside the Pod
kubectl exec -it -n microtask statefulset/mysql -- mysql -u microtask_user -pmicrotask_pass microtask_db

# Inside MySQL:
# SHOW TABLES;
# SELECT id, title, status, priority FROM tasks;
# SELECT * FROM task_history LIMIT 10;
# EXIT;
```

---

## Step 12 — Helm upgrade

After changing values (e.g. increase worker replicas or change FAILURE_RATE):

```powershell
# After editing values-dev.yaml:
helm upgrade microtask helm/microtask -f helm/microtask/values-dev.yaml -n microtask

# Check rollout status
kubectl rollout status deployment/worker -n microtask
kubectl rollout status deployment/api -n microtask
```

---

## Step 13 — Helm rollback

```powershell
# View release history
helm history microtask -n microtask

# Rollback to previous revision
helm rollback microtask 1 -n microtask

# Verify rollback
helm status microtask -n microtask
kubectl get pods -n microtask
```

---

## Step 14 — Troubleshooting failed Pods

```powershell
# Describe a Pod to see events and error messages
kubectl describe pod -n microtask <pod-name>

# Check previous container logs (if Pod crashed and restarted)
kubectl logs -n microtask <pod-name> --previous

# Get events sorted by time
kubectl get events -n microtask --sort-by='.lastTimestamp'

# Check if images loaded correctly in Minikube
minikube image ls | Select-String "microtask"

# If a Pod is stuck in Pending — check PVC
kubectl describe pvc mysql-pvc -n microtask

# If API Pod is CrashLoopBackOff — check logs
kubectl logs -n microtask deployment/api

# If migration Job failed — check logs and re-run
kubectl logs -n microtask job/microtask-migrate
# Delete and re-run the job manually:
kubectl delete job microtask-migrate -n microtask
```

---

## Step 15 — Uninstall

```powershell
# Uninstall the Helm release (removes all Kubernetes resources)
helm uninstall microtask -n microtask

# The PVC is NOT deleted automatically (protects your data)
# To also delete the PVC and MySQL data:
kubectl delete pvc mysql-pvc -n microtask

# Delete the namespace (removes everything including PVCs)
kubectl delete namespace microtask
```

---

## Step 16 — Stop Minikube

```powershell
# Stop Minikube (preserves cluster state)
minikube stop

# Delete Minikube cluster entirely (frees all disk space)
minikube delete
```

> Your Docker Compose application and its mysql_data volume are completely separate
> from Minikube. Stopping or deleting Minikube does NOT affect your Docker Compose setup.

---

## Architecture inside Kubernetes

```
Browser
  |
  | kubectl port-forward 3000:80
  v
frontend Pod (Nginx:80)
  |
  | proxy_pass http://api:8000  (Kubernetes DNS)
  v
api Pod (FastAPI:8000)
  |
  | MYSQL_HOST=mysql  (Kubernetes DNS)
  v
mysql-0 Pod (MySQL:3306)
  ^
  |
worker Pod (polls mysql every 5s)
```

All internal communication uses Kubernetes ClusterIP Services resolved by DNS.
Only the frontend is exposed externally via NodePort 30080 or port-forward.
