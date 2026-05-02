#!/bin/bash
# Run this ONCE on the EC2 server after k3s is up.
# It creates the two Kubernetes secrets the app needs.
# Nothing here is committed — secrets live only in the cluster.

set -e

NAMESPACE="hzortech"

echo "[setup] Creating namespace..."
kubectl apply -f /opt/hzortech/k8s/00-namespace.yaml

echo "[setup] Creating hzortech-secrets..."
kubectl create secret generic hzortech-secrets \
  --namespace "$NAMESPACE" \
  --from-literal=DJANGO_SECRET_KEY="$(openssl rand -base64 50)" \
  --from-literal=POSTGRES_PASSWORD="$(openssl rand -base64 32)" \
  --from-literal=EMAIL_HOST_USER="shara@hzortech.com" \
  --from-literal=EMAIL_HOST_PASSWORD="gssi miem lchd wpek" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "[setup] Done. Secrets are stored in-cluster only."
echo ""
echo "Next: push to master — GitHub Actions will build the image,"
echo "apply manifests, and roll out the deployment automatically."
