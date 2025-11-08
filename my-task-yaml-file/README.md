# Kubernetes Resources YAML Files

This directory contains all Kubernetes resources exported from the cluster, organized by namespace.

## 📁 Directory Structure

```
my-task-yaml-file/
├── bitpin-task/          # Application namespace resources
├── monitoring/           # Monitoring namespace resources
├── logging/              # Logging namespace resources
└── cnpg-system/          # CloudNativePG operator namespace resources
```

## 📊 Resource Count by Namespace

### bitpin-task Namespace
- **Total Files**: 70+ resources
- **Resource Types**:
  - Deployments: bitpin-app
  - Services: bitpin-app-svc, bitpin-cluster-* (3 services)
  - PostgreSQL Cluster: bitpin-cluster (CloudNativePG)
  - CronJobs: 8 backup cronjobs
  - Jobs: 30+ backup and test jobs
  - ConfigMaps: 3
  - Secrets: 5 (database credentials)
  - PersistentVolumeClaims: 5
  - ReplicaSets: 11
  - Ingresses: 3
  - ServiceAccounts: 2
  - Roles & RoleBindings: 2
  - PodDisruptionBudgets: 1

### monitoring Namespace
- **Total Files**: 200+ resources
- **Resource Types**:
  - StatefulSets: Prometheus, Alertmanager
  - Deployments: Grafana, kube-state-metrics, Prometheus Operator
  - DaemonSets: Node Exporter
  - Services: 13 services
  - ConfigMaps: 40+ (Grafana dashboards, Prometheus configs)
  - Secrets: 12 (TLS certificates, web configs)
  - Prometheus CRDs: Prometheus, Alertmanager, ServiceMonitors, PodMonitors, PrometheusRules
  - ReplicaSets: 13
  - ServiceAccounts: 7
  - Roles & RoleBindings: 2
  - Ingresses: 3

### logging Namespace
- **Total Files**: 30+ resources
- **Resource Types**:
  - StatefulSet: Loki (log storage)
  - Deployment: Loki Grafana
  - DaemonSet: Promtail (log collection)
  - Services: 4 (Loki, Loki Grafana, headless, memberlist)
  - ConfigMaps: 4
  - Secrets: 4
  - PersistentVolumeClaims: 1
  - ReplicaSets: 1
  - ServiceAccounts: 4
  - Roles & RoleBindings: 4
  - Ingress: 1

### cnpg-system Namespace
- **Total Files**: 10+ resources
- **Resource Types**:
  - Deployment: CloudNativePG operator
  - Service: Webhook service
  - ConfigMaps: 3
  - Secrets: 3 (CA, webhook certificates)
  - ReplicaSets: 1
  - ServiceAccounts: 2

## 📝 File Naming Convention

Files are named using the pattern: `<resource-type>-<resource-name>.yaml`

Examples:
- `deployments-bitpin-app-yaml`
- `services-bitpin-app-svc-yaml`
- `clusters-postgresql-cnpg-io-bitpin-cluster-yaml`
- `prometheuses-monitoring-coreos-com-prometheus-kube-prometheus-prometheus-yaml`

## 🔍 Resource Categories

### Application Resources (bitpin-task)
- **Application**: Django-based cryptocurrency exchange
- **Database**: PostgreSQL cluster with High Availability
- **Backups**: Automated full and incremental backups
- **Networking**: Services, Ingresses for external access

### Monitoring Resources (monitoring)
- **Metrics Collection**: Prometheus StatefulSet
- **Alerting**: Alertmanager StatefulSet
- **Visualization**: Grafana Deployment
- **Node Metrics**: Node Exporter DaemonSet
- **K8s Metrics**: kube-state-metrics Deployment
- **Configuration**: ServiceMonitors, PodMonitors, PrometheusRules

### Logging Resources (logging)
- **Log Storage**: Loki StatefulSet
- **Log Collection**: Promtail DaemonSet
- **Log Visualization**: Grafana Deployment
- **Configuration**: ConfigMaps for Loki and Grafana

### Operator Resources (cnpg-system)
- **PostgreSQL Operator**: CloudNativePG operator deployment
- **Webhooks**: Admission webhooks for cluster management
- **Configuration**: Operator configuration and certificates

## 🚀 Usage

These YAML files can be used to:
1. **Documentation**: Understand the complete infrastructure setup
2. **Backup**: Keep a snapshot of all resources
3. **Migration**: Recreate resources in another cluster
4. **Audit**: Review all configurations
5. **Presentation**: Show complete infrastructure to stakeholders

## 📋 Notes

- All files are exported from the live cluster
- Each resource is saved as a separate YAML file
- Files include all metadata and status information
- Secrets may contain sensitive data - handle with care
- Some resources may have cluster-specific references

## 🔗 Related Documentation

- See `/app/` directory for namespace descriptions
- See `/general/README.md` for deployment instructions
- See `/general/helm/` for Helm charts

---

**Total Resources Exported**: 267+ YAML files
**Last Updated**: $(date)

