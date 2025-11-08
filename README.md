# Bitpin Task - Kubernetes Deployment

This repository contains the complete Kubernetes deployment configuration for the Bitpin cryptocurrency exchange application, including Helm charts, CI/CD pipelines, monitoring, and logging solutions.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [Database Backup](#database-backup)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This project implements a production-ready Kubernetes deployment for a Django-based cryptocurrency exchange application. The infrastructure includes:

- **Application**: Django/Python backend application
- **Database**: PostgreSQL with CloudNativePG (Primary + Replica setup)
- **Load Balancing**: NodePort service with Ingress support
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki + Grafana + Promtail
- **CI/CD**: GitHub Actions for automated build and deployment
- **Backup**: Automated database backup with CronJobs

## 🏗️ Architecture

### Infrastructure Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           bitpin-task Namespace                      │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │  bitpin-app  │  │  PostgreSQL  │                │   │
│  │  │  (Django)    │◄─┤  Cluster     │                │   │
│  │  │              │  │  (Primary +  │                │   │
│  │  │  Deployment  │  │   Replica)   │                │   │
│  │  └──────┬───────┘  └──────────────┘                │   │
│  │         │                                            │   │
│  │  ┌──────▼───────┐  ┌──────────────┐                │   │
│  │  │   Service    │  │  Backup      │                │   │
│  │  │  (NodePort)  │  │  CronJobs    │                │   │
│  │  └──────────────┘  └──────────────┘                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           monitoring Namespace                       │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │  Prometheus  │  │   Grafana     │                │   │
│  │  │  (Metrics)   │◄─┤  (Dashboards) │                │   │
│  │  └──────────────┘  └──────────────┘                │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │ Alertmanager │  │ Node Exporter │                │   │
│  │  └──────────────┘  └──────────────┘                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           logging Namespace                          │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │    Loki      │  │   Grafana    │                │   │
│  │  │  (Log Store) │◄─┤  (Log View)  │                │   │
│  │  └──────▲───────┘  └──────────────┘                │   │
│  │         │                                            │   │
│  │  ┌──────┴───────┐                                    │   │
│  │  │  Promtail    │                                    │   │
│  │  │ (Log Agent)  │                                    │   │
│  │  └──────────────┘                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Namespace Descriptions

#### bitpin-task Namespace
- **Purpose**: Main application namespace
- **Resources**:
  - `bitpin-app`: Django application deployment
  - `bitpin-cluster`: PostgreSQL cluster (CloudNativePG)
  - Services: Application service (NodePort), Database services (RW, RO, R)
  - CronJobs: Automated database backups (full and incremental)

#### monitoring Namespace
- **Purpose**: Metrics collection and visualization
- **Resources**:
  - Prometheus: Metrics collection and storage
  - Grafana: Metrics visualization and dashboards
  - Alertmanager: Alert management
  - Node Exporter: Node-level metrics
  - Kube-state-metrics: Kubernetes object metrics

#### logging Namespace
- **Purpose**: Centralized log aggregation
- **Resources**:
  - Loki: Log storage and indexing
  - Grafana: Log visualization
  - Promtail: Log collection agent (DaemonSet)

## 📁 Directory Structure

```
bitpin-task-full/
├── general/                          # Main deployment files
│   ├── helm/                         # Helm charts
│   │   └── bitpin-app/              # Application Helm chart
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       └── templates/
│   │           ├── deployment.yaml
│   │           ├── service.yaml
│   │           ├── ingress.yaml
│   │           ├── hpa.yaml
│   │           └── _helpers.tpl
│   ├── .github/                      # CI/CD workflows
│   │   └── workflows/
│   │       ├── ci-cd.yml            # Main CI/CD pipeline
│   │       └── backup-job.yml       # Backup automation
│   ├── *.yaml                        # Kubernetes resource files
│   │   ├── bitpin-app-deployment.yaml
│   │   ├── bitpin-app-service.yaml
│   │   ├── bitpin-postgres-cluster.yaml
│   │   ├── bitpin-backup-cronjobs.yaml
│   │   ├── bitpin-task-resources.yaml
│   │   ├── logging-resources.yaml
│   │   └── monitoring-resources.yaml
│   └── README.md                     # This file
└── app/                              # Application-specific files
    ├── bitpin-task-namespace-description.txt
    ├── logging-namespace-description.txt
    └── monitoring-namespace-description.txt
```

## 🚀 Deployment

### Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3.x installed
- Docker (for building images)
- CloudNativePG operator (for PostgreSQL cluster)

### Step 1: Install CloudNativePG Operator

```bash
kubectl apply -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml
```

### Step 2: Deploy PostgreSQL Cluster

```bash
kubectl apply -f general/bitpin-postgres-cluster.yaml
```

Wait for the cluster to be ready:
```bash
kubectl wait --for=condition=Ready cluster/bitpin-cluster -n bitpin-task --timeout=300s
```

### Step 3: Deploy Application with Helm

```bash
# Install the Helm chart
helm install bitpin-app ./general/helm/bitpin-app \
  --namespace bitpin-task \
  --create-namespace

# Or upgrade if already installed
helm upgrade --install bitpin-app ./general/helm/bitpin-app \
  --namespace bitpin-task \
  --create-namespace
```

### Step 4: Verify Deployment

```bash
# Check application pods
kubectl get pods -n bitpin-task

# Check services
kubectl get svc -n bitpin-task

# Check application logs
kubectl logs -f deployment/bitpin-app -n bitpin-task
```

### Step 5: Access the Application

The application is exposed via NodePort service. Get the node IP and port:

```bash
# Get node IP
kubectl get nodes -o wide

# Get service port
kubectl get svc bitpin-app-svc -n bitpin-task

# Access: http://<NODE_IP>:<NODE_PORT>
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

#### Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers:**
- Push to main/master branch
- Pull requests to main/master

**Jobs:**
1. **Build and Push**: Builds Docker image and pushes to registry
2. **Deploy**: Deploys application to Kubernetes using Helm
3. **Lint Helm**: Validates Helm chart syntax

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
   ```bash
   # In GitHub repository: Settings > Secrets and variables > Actions
   DOCKER_USERNAME=your-username
   DOCKER_PASSWORD=your-token
   KUBECONFIG=$(cat ~/.kube/config | base64 -w 0)
   ```

2. **Push to trigger pipeline:**
   ```bash
   git push origin main
   ```

## 📊 Monitoring & Logging

### Accessing Monitoring Dashboards

#### Prometheus
```bash
# Port forward to access Prometheus
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
# Access: http://localhost:9090
```

#### Grafana (Monitoring)
```bash
# Port forward to access Grafana
kubectl port-forward svc/grafana -n monitoring 3000:3000
# Access: http://localhost:3000
# Default credentials: admin/admin (change on first login)
```

#### Grafana (Logging)
```bash
# Port forward to access Loki Grafana
kubectl port-forward svc/loki-grafana -n logging 3001:80
# Access: http://localhost:3001
```

### Key Metrics

- Application health and availability
- Database connection pool metrics
- Request latency and throughput
- Resource utilization (CPU, Memory)
- Pod restart counts

### Log Aggregation

- Application logs collected by Promtail
- Stored in Loki
- Queryable via Grafana LogQL

## 💾 Database Backup

### Backup Strategy

The deployment includes multiple backup mechanisms:

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
# Check pod status
kubectl get pods -n bitpin-task

# Check pod logs
kubectl logs -f deployment/bitpin-app -n bitpin-task

# Check events
kubectl describe pod <pod-name> -n bitpin-task
```

### Database Connection Issues

```bash
# Check database cluster status
kubectl get cluster -n bitpin-task

# Check database pods
kubectl get pods -n bitpin-task | grep cluster

# Test database connection
kubectl exec -it bitpin-cluster-1 -n bitpin-task -- psql -U bitpin_user -d bitpin_db
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n bitpin-task

# Check service configuration
kubectl describe svc bitpin-app-svc -n bitpin-task

# Test service from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://bitpin-app-svc.bitpin-task.svc.cluster.local/healthz/
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

