# Repository instructions

This repository deploys Changedetection and its Sockpuppet browser dependency to
Kubernetes/K3s. It is a Kubernetes installer repository, not an Ansible Galaxy
role.

## Ownership and safety

- Treat the configured namespace as a managed cluster target.
- Changedetection and Sockpuppet are co-located application components; do not
  expose Sockpuppet outside its ClusterIP Service.
- DNS, public TLS, ingress-controller installation, credentials, notification
  URLs, and backups are operator-owned external dependencies.
- Do not use `:latest`, mutable backup tooling, broad filesystem permissions, or
  timing-based scale-down backup jobs.
- Do not commit kubeconfigs, credentials, notification URLs, certificates,
  private addresses, or rendered environment-specific manifests.

## Required verification

```bash
python3 tests/test_manifests.py
kubectl apply --dry-run=server -f runtime/
kubectl -n "$NAMESPACE" rollout status deployment/changedetection --timeout=300s
kubectl -n "$NAMESPACE" rollout status deployment/sockpuppet --timeout=300s
```

Live QA must use an explicitly disposable namespace. Verify application and
browser readiness, PVC binding, second-apply convergence, and exact namespace
cleanup. Use only the approved SSH path/account for target access.
