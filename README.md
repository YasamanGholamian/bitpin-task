# Bitpin Task - Kubernetes Deployment

This repository contains Kubernetes manifests, Helm charts, and CI/CD pipelines for deploying the Bitpin cryptocurrency exchange application.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Deployment](#deployment)
- [CI/CD](#cicd)
- [Monitoring & Logging](#monitoring--logging)
- [Backup Strategy](#backup-strategy)

## 🎯 Overview

This project deploys a Django-based cryptocurrency exchange application on Kubernetes with:
- PostgreSQL database cluster (CloudNativePG)
- Automated backups
- Monitoring (Prometheus + Grafana)
- Logging (Loki + Grafana)
- CI/CD pipeline (GitHub Actions)

## 🏗️ Architecture

```
┌─────────────────┐
│   LoadBalancer  │
│   / Ingress     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   bitpin-app    │────▶│  PostgreSQL     │
│   (Django)       │     │  Cluster        │
│   Deployment    │     │  (Primary+Replica)│
└─────────────────┘     └─────────────────┘
         │
         ├─────────────────┐
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│   Prometheus    │  │      Loki        │
│   (Metrics)     │  │   (Logs)        │
└─────────────────┘  └─────────────────┘
```

## 📁 Directory Structure

```
general/
├── helm/
│   └── bitpin-app/          # Helm chart for application
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── hpa.yaml
│           └── _helpers.tpl
├── .github/
│   └── workflows/
│       ├── ci-cd.yml        # Main CI/CD pipeline
│       └── backup-job.yml   # Backup automation
├── bitpin-app-deployment.yaml
├── bitpin-app-service.yaml
├── bitpin-postgres-cluster.yaml
├── bitpin-backup-cronjobs.yaml
├── bitpin-task-namespace.yaml
├── logging-resources.yaml
├── monitoring-resources.yaml
└── README.md
```

## 🚀 Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3.x installed
- CloudNativePG operator installed
- Docker (for building images)
- GitHub repository with secrets configured

## 📦 Deployment

### Step 1: Install CloudNativePG Operator

```bash
kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml
```

### Step 2: Deploy PostgreSQL Cluster

```bash
kubectl apply -f bitpin-postgres-cluster.yaml
kubectl wait --for=condition=Ready cluster/bitpin-cluster -n bitpin-task --timeout=300s
```

### Step 3: Deploy Application with Helm

```bash
# Install the Helm chart
helm install bitpin-app ./helm/bitpin-app \
  --namespace bitpin-task \
  --create-namespace

# Or upgrade if already installed
helm upgrade --install bitpin-app ./helm/bitpin-app \
  --namespace bitpin-task \
  --create-namespace
```

### Step 4: Verify Deployment

```bash
kubectl get pods -n bitpin-task
kubectl get svc -n bitpin-task
kubectl logs -f deployment/bitpin-app -n bitpin-task
```

## 🔄 CI/CD

### GitHub Actions Workflows

#### Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers:**
- Push to main/master branch
- Pull requests to main/master
- Manual trigger (workflow_dispatch)

**Jobs:**
1. **Build and Push**: Builds Docker image and pushes to Docker Hub
2. **Lint Helm**: Validates Helm chart syntax
3. **Deploy**: Deploys application to Kubernetes using Helm

**Required Secrets:**
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password/token
- `KUBECONFIG`: Base64-encoded kubeconfig file

#### Backup Job (`.github/workflows/backup-job.yml`)

**Triggers:**
- Daily at 2 AM UTC (cron schedule)
- Manual trigger (workflow_dispatch)

**Function:**
- Triggers database backup CronJob
- Waits for backup completion

### Setting Up CI/CD

1. **Add GitHub Secrets:**
   - Go to: Settings > Secrets and variables > Actions
   - Add:
     - `DOCKER_USERNAME`: your-username
     - `DOCKER_PASSWORD`: your-token
     - `KUBECONFIG`: `$(cat ~/.kube/config | base64 -w 0)`

2. **Push to trigger pipeline:**
   ```bash
   git push origin main
   ```

## 📊 Monitoring & Logging

### Accessing Dashboards

#### Prometheus
```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Access: http://localhost:9090
```

#### Grafana (Monitoring)
```bash
kubectl port-forward svc/grafana -n monitoring 3000:3000
# Access: http://localhost:3000
# Default: admin/admin
```

#### Grafana (Logging)
```bash
kubectl port-forward svc/loki-grafana -n logging 3001:80
# Access: http://localhost:3001
```

### Key Metrics

- Application health and availability
- Database connection pool metrics
- Request latency and throughput
- Resource utilization (CPU, Memory)
- Pod restart counts

## 💾 Backup Strategy

### Backup Mechanisms

1. **Full Backup CronJob**: Runs daily at 2 AM UTC
   - Job: `bitpin-full-backup`
   - Creates complete database dump

2. **Incremental Backup CronJob**: Runs every 15 minutes
   - Job: `bitpin-incremental-backup`
   - WAL (Write-Ahead Log) archiving

3. **Manual Backup**: Trigger via GitHub Actions or kubectl
   ```bash
   kubectl create job --from=cronjob/bitpin-full-backup manual-backup-$(date +%Y%m%d-%H%M%S) -n bitpin-task
   ```

### Backup Location

Backups are stored in persistent volumes. Check backup jobs:
```bash
kubectl get jobs -n bitpin-task | grep backup
kubectl logs job/<backup-job-name> -n bitpin-task
```

## 🔧 Configuration

### Helm Values

Edit `helm/bitpin-app/values.yaml` to customize:
- Replica count
- Resource limits/requests
- Service type and ports
- Environment variables
- Database connection settings
- Health check probes

### Example Customization

```yaml
# Scale application
replicaCount: 3

# Enable autoscaling
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5

# Enable ingress
ingress:
  enabled: true
  hosts:
    - host: bitpin.example.com
      paths:
        - path: /
          pathType: Prefix
```

## 🐛 Troubleshooting

### Application Not Starting

```bash
kubectl get pods -n bitpin-task
kubectl logs -f deployment/bitpin-app -n bitpin-task
kubectl describe pod <pod-name> -n bitpin-task
```

### Database Connection Issues

```bash
kubectl get cluster -n bitpin-task
kubectl get pods -n bitpin-task | grep cluster
kubectl exec -it bitpin-cluster-1 -n bitpin-task -- psql -U bitpin_user -d bitpin_db
```

### Service Not Accessible

```bash
kubectl get endpoints -n bitpin-task
kubectl describe svc bitpin-app-svc -n bitpin-task
```

## 📝 Additional Resources

- [CloudNativePG Documentation](https://cloudnative-pg.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of the Bitpin interview task.

## 🔗 Links

- **Repository**: https://github.com/YasamanGholamian/bitpin-task
- **Application Source**: https://github.com/MGasiorowskii/CryptoCurrencyExchange

---

**Note**: This deployment is configured for a development/testing environment. For production, consider:
- Using Ingress with TLS certificates
- Implementing resource quotas and limits
- Setting up network policies
- Configuring backup retention policies
- Enabling monitoring alerts
- Implementing proper secret management
