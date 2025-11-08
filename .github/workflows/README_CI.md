# CI/CD (GitLab & GitHub) — Quickstart

## Overview
This repo contains:
- `.gitlab-ci.yml` — GitLab CI pipeline (lint, build, test, push, deploy)
- `.github/workflows/ci-cd.yml` — GitHub Actions equivalent
- k8s manifests in `k8s/` (deployment, service, ingress)

## Prerequisites
- Docker Hub account (or change registry to your private registry)
- Kubeconfig for target cluster (base64 encoded)
- GitLab project with CI enabled OR GitHub repo with Actions enabled

## Required CI variables (GitLab)
Set these in Project → Settings → CI/CD → Variables (Protected + Masked where appropriate):
- `DOCKER_USERNAME` — Docker Hub user
- `DOCKER_PASSWORD` — Docker Hub password
- `IMAGE_NAME` — e.g. `yasaman664/bitpin-task`
- `KUBECONFIG_DATA` — `base64 < ~/.kube/config` output (base64-encoded)
- `K8S_NAMESPACE` — e.g. `bitpin-task`
- `DJANGO_SETTINGS_MODULE` — default `Exchange.settings`

## Required Secrets (GitHub Actions)
Add repository secrets:
- `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `KUBECONFIG_DATA`, optionally `K8S_NAMESPACE`

## How to install CI files
1. Place `.gitlab-ci.yml` at repo root.
2. Place `.github/workflows/ci-cd.yml` at `.github/workflows/ci-cd.yml`.
3. Ensure `k8s/` directory contains your `deployment.yaml` and `service.yaml` (the pipeline will `kubectl set image` on `deployment/bitpin-task`).
4. Commit & push.

## How pipeline works (summary)
- **lint**: flake8 (optional)
- **build**: docker build (tagged with commit short SHA)
- **test**: install deps and run Django tests (pytest/manage.py test)
- **push**: push images to docker.io (for main/master branches)
- **deploy**: set image to deployment and wait for rollout

## Manual test (locally)
1. Build and push image:
   ```bash
   docker build -t docker.io/yasaman664/bitpin-task:local-test .
   docker push docker.io/yasaman664/bitpin-task:local-test
