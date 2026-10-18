#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
namespace=${NAMESPACE:-cloudnotes-rescue}
# Instructor runs only against the intended disposable local assessment cluster.
kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
# Random disposable practice value, generated without exposing it in terminal output.
python3 -c 'import secrets; print(secrets.token_hex(24), end="")' | kubectl -n "$namespace" create secret generic cloudnotes-access --from-file=API_TOKEN=/dev/stdin --dry-run=client -o yaml | kubectl apply -f -
kubectl -n "$namespace" apply -f k8s/
kubectl -n "$namespace" wait --for=condition=Ready pod/client --timeout=90s
kubectl -n "$namespace" get pods,pvc
