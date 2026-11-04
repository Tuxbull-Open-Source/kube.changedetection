# kube.changedetection

Deploy [changedetection.io](https://changedetection.io/) and its optional
Sockpuppet Playwright/Chrome service on k3s or Kubernetes.

The deployment owns one namespace containing the Changedetection application,
its persistent data, and its browser dependency. It does **not** manage DNS,
public TLS certificates, an ingress controller, or backup infrastructure.

## Release 1.0.0

Images are pinned to immutable multi-architecture image-index digests:

- Changedetection `0.60.10`
- Sockpuppetbrowser `0.0.3`

Do not replace the digests with `latest`. Review upstream release and migration
notes before selecting new image versions.

## Prerequisites

- A Ready Kubernetes/K3s cluster with the `local-path` StorageClass.
- An existing Traefik IngressClass.
- Operator-managed DNS and HTTPS termination for the selected FQDN. The shipped
  Ingress intentionally contains no TLS Secret, certificate, issuer, or ACME
  configuration.
- `kubectl` configured for the intended cluster.

## Render and review

Use a dedicated namespace and a valid DNS hostname. Generated files contain no
credentials but are environment-specific and should not be committed.

```bash
export NAMESPACE=changedetection
export FQDN=changedetection.example.com

rm -rf runtime
install -d -m 0700 runtime
for manifest in *.yml; do
  sed -e "s/__NAMESPACE__/${NAMESPACE}/g" \
      -e "s/__FQDN__/${FQDN}/g" \
      "$manifest" > "runtime/$manifest"
done

grep -R '__NAMESPACE__\|__FQDN__' runtime && exit 1
# A server-side dry run cannot create the Namespace, so create/reconcile that
# exact namespace first, then validate its namespaced resources.
kubectl apply -f runtime/01_namespace.yml
for manifest in runtime/0[2-7]_*.yml; do
  kubectl apply --dry-run=server -f "$manifest"
done
```

Review the rendered manifests, then apply in filename order:

```bash
for manifest in runtime/*.yml; do
  kubectl apply -f "$manifest"
done

kubectl -n "$NAMESPACE" rollout status deployment/changedetection --timeout=300s
kubectl -n "$NAMESPACE" rollout status deployment/sockpuppet --timeout=300s
kubectl -n "$NAMESPACE" get deployment,pod,service,pvc,ingress
```

## Operation

Changedetection uses Sockpuppet through the cluster-local endpoint:

```text
ws://sockpuppet:3000/?--window-size=1920,1080
```

Sockpuppet is required only for browser/Playwright fetches. It is deliberately a
ClusterIP-only service and is not externally exposed.

The Changedetection deployment uses `Recreate` because `local-path` PVCs are
single-writer `ReadWriteOnce`. Do not scale Changedetection above one replica.

## Backup and recovery

The old in-cluster backup CronJob was removed. It used mutable images, broad
`chmod -R 777`, fixed sleep intervals, and no restore verification. Use the
cluster's supported backup mechanism (for example Velero) to back up the
namespace and `changedetection-data` PVC. Require a recent successful backup
and an isolated restore rehearsal before image upgrades or destructive work.

## QA

Use an explicitly disposable namespace such as `qa`. Do not use a production
namespace. QA verifies both workloads become Ready, the PVC becomes Bound, the
Changedetection HTTP endpoint responds from inside the Pod, Sockpuppet accepts
TCP connections, and a second apply converges.

Delete the exact QA namespace after testing:

```bash
kubectl delete namespace qa --wait=true
```

## Security boundaries

- Never place credentials, notification URLs, API tokens, private certificates,
  or kubeconfigs in this repository.
- Configure authentication and notification secrets through an approved secret
  manager or a separately managed Kubernetes Secret; they are not modelled by
  these manifests.
- The public ingress requires operator-managed HTTPS. Do not expose Sockpuppet
  directly.
