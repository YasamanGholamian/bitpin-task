# Architecture Documentation

## System Architecture Overview

### High-Level Architecture

The Bitpin cryptocurrency exchange application is deployed on Kubernetes with a microservices-oriented architecture, focusing on scalability, reliability, and observability.

## Component Details

### 1. Application Layer (bitpin-task namespace)

#### Django Application (bitpin-app)
- **Type**: Deployment
- **Replicas**: 1 (configurable via Helm)
- **Image**: `yasaman664/bitpin-task:latest`
- **Port**: 8000
- **Health Checks**:
  - Liveness: `/healthz/` endpoint, 10s initial delay, 20s period
  - Readiness: `/healthz/` endpoint, 5s initial delay, 10s period

**Environment Variables:**
- `DJANGO_SETTINGS_MODULE`: Exchange.settings
- Database connection via secrets (host, port, dbname, user, password)

**Volumes:**
- Static files: `/app/Exchange/static` (emptyDir)
- Media files: `/app/Exchange/media` (emptyDir)

#### Service (bitpin-app-svc)
- **Type**: NodePort
- **Port**: 80 → 8000
- **NodePort**: 30505
- **Selector**: app=bitpin-app

### 2. Database Layer

#### PostgreSQL Cluster (bitpin-cluster)
- **Operator**: CloudNativePG
- **Instances**: 2 (Primary + Replica)
- **Image**: `ghcr.io/cloudnative-pg/postgresql:15.3`
- **Storage**: 5Gi per instance
- **High Availability**: Enabled with replication slots

**Services:**
- `bitpin-cluster-rw`: Read-Write service (Primary)
- `bitpin-cluster-ro`: Read-Only service (Replicas)
- `bitpin-cluster-r`: Read service (All instances)

**Features:**
- Automatic failover
- WAL archiving enabled
- Logical replication
- Connection pooling ready

### 3. Backup Strategy

#### Full Backup
- **Schedule**: Daily at 2:00 AM UTC
- **CronJob**: `bitpin-full-backup`
- **Type**: Complete database dump

#### Incremental Backup
- **Schedule**: Every 15 minutes
- **CronJob**: `bitpin-incremental-backup`
- **Type**: WAL archiving

### 4. Monitoring Stack (monitoring namespace)

#### Prometheus
- **Purpose**: Metrics collection and storage
- **Retention**: Configurable
- **Scrape Interval**: 15s (default)
- **Targets**:
  - Kubernetes API
  - Node metrics
  - Application metrics (if instrumented)
  - Database metrics

#### Grafana
- **Purpose**: Metrics visualization
- **Port**: 3000
- **Data Sources**:
  - Prometheus
  - Loki (for logs)

#### Alertmanager
- **Purpose**: Alert routing and management
- **Integration**: Can send alerts to various channels

#### Node Exporter
- **Type**: DaemonSet
- **Purpose**: Node-level metrics collection
- **Port**: 9100

#### Kube-state-metrics
- **Purpose**: Kubernetes object metrics
- **Metrics**: Deployment, Pod, Service states

### 5. Logging Stack (logging namespace)

#### Loki
- **Type**: StatefulSet
- **Purpose**: Log storage and indexing
- **Port**: 3100
- **Storage**: Persistent volumes

#### Promtail
- **Type**: DaemonSet
- **Purpose**: Log collection agent
- **Function**: Scrapes logs from all pods and sends to Loki

#### Grafana (Logging)
- **Purpose**: Log visualization and querying
- **Port**: 80 (NodePort: 30030)
- **Data Source**: Loki

## Data Flow

### Application Request Flow
```
User Request
    ↓
NodePort Service (30505)
    ↓
bitpin-app-svc (ClusterIP)
    ↓
bitpin-app Pod
    ↓
Django Application
    ↓
Database (bitpin-cluster-rw)
```

### Metrics Flow
```
Application/Infrastructure
    ↓
Prometheus (scraping)
    ↓
Grafana (visualization)
```

### Logs Flow
```
Application Pods
    ↓
Promtail (DaemonSet - collects logs)
    ↓
Loki (stores logs)
    ↓
Grafana (queries and visualizes)
```

## Network Architecture

### Service Discovery
- Services use Kubernetes DNS
- Format: `<service-name>.<namespace>.svc.cluster.local`
- Example: `bitpin-app-svc.bitpin-task.svc.cluster.local`

### Network Policies
Currently not implemented. For production, consider:
- Restrict database access to application namespace only
- Isolate monitoring and logging namespaces
- Implement pod-to-pod communication rules

## Storage Architecture

### Application Storage
- **Static/Media**: EmptyDir (ephemeral)
- **Recommendation**: Use PersistentVolumes for production

### Database Storage
- **Type**: PersistentVolumeClaims
- **Size**: 5Gi per instance
- **Storage Class**: Default (cluster-specific)

### Backup Storage
- Stored in persistent volumes
- Retention policy: Configurable via CronJob

## Security Considerations

### Current Implementation
- Secrets managed via Kubernetes Secrets
- Database credentials stored in `bitpin-cluster-app` secret
- TLS enabled for database connections

### Production Recommendations
- Use external secret management (e.g., Sealed Secrets, External Secrets Operator)
- Implement network policies
- Enable Pod Security Standards
- Use service accounts with minimal permissions
- Implement RBAC for namespace access
- Enable audit logging

## Scalability

### Horizontal Scaling
- Application: Can scale via HPA (configured in Helm chart)
- Database: Read replicas can be added (CloudNativePG supports this)

### Vertical Scaling
- Resource limits/requests configurable via Helm values
- Database resources configurable in Cluster spec

## High Availability

### Application
- Multiple replicas supported
- Rolling updates configured
- Health checks ensure only healthy pods serve traffic

### Database
- Primary-Replica setup
- Automatic failover
- Replication slots for high availability
- WAL archiving for point-in-time recovery

## Disaster Recovery

### Backup Strategy
1. **Full Backups**: Daily complete dumps
2. **Incremental Backups**: WAL archiving every 15 minutes
3. **Retention**: Configurable

### Recovery Procedures
1. Restore from full backup
2. Apply WAL archives for point-in-time recovery
3. Verify data integrity
4. Update application configuration if needed

## Performance Considerations

### Application
- Health check intervals optimized
- Resource requests/limits should be set based on load testing
- Consider implementing caching layer (Redis)

### Database
- Connection pooling recommended
- Read replicas for read-heavy workloads
- Query optimization at application level

### Monitoring
- Prometheus retention should be balanced with storage
- Grafana dashboards optimized for performance
- Alert rules should not cause alert fatigue

## Future Enhancements

1. **Ingress Controller**: Replace NodePort with Ingress + TLS
2. **Redis Cache**: Add caching layer for improved performance
3. **Message Queue**: For async task processing
4. **Service Mesh**: Istio/Linkerd for advanced traffic management
5. **GitOps**: ArgoCD/Flux for declarative deployments
6. **Secrets Management**: External secrets operator
7. **Network Policies**: Implement pod-to-pod security
8. **Resource Quotas**: Per-namespace resource limits
9. **Multi-region**: For global availability
10. **CDN**: For static asset delivery

