# Changelog

## [1.0.0] - 2026-11-04

### Changed

- Modernize raw Kubernetes manifests for the `Tuxbull-Open-Source` namespace.
- Pin Changedetection `0.60.10` and Sockpuppetbrowser `0.0.3` to immutable
  multi-architecture image-index digests.
- Add consistent ownership labels, resource requests/limits, TCP probes, and
  `RuntimeDefault` seccomp profiles.
- Use a Recreate strategy for the single-writer local-path PVC.
- Configure `BASE_URL` and the upstream recommended Playwright driver URL.
- Replace legacy resource names with stable `changedetection` and
  `changedetection-data` names.
- Remove the unsafe in-cluster backup CronJob, broad permissions, mutable backup
  images, and unverified local archive retention path.
- Rewrite operator documentation with render/review, rollout, backup/recovery,
  and QA boundaries.

### QA

- Static manifest parsing and rendered server-side validation are required.
- Live QA in an explicitly disposable namespace must verify both workloads,
  persistent storage, internal application connectivity, browser endpoint
  reachability, second-apply convergence, and namespace cleanup.
