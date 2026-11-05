#!/usr/bin/env python3
"""Static safety checks for the Changedetection Kubernetes manifests."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = sorted(ROOT.glob("*.yml"))
OWNERSHIP = "kube.changedetection"


def docs(path):
    return [d for d in yaml.safe_load_all(path.read_text()) if d]


def by_kind_name(items, kind, name):
    return next(d for d in items if d["kind"] == kind and d["metadata"]["name"] == name)


def main():
    assert not list(ROOT.glob("11_backup_*.yml"))
    assert not list(ROOT.glob("12_backup_*.yml"))
    assert not list(ROOT.glob("13_backup_*.yml"))
    items = [d for p in MANIFESTS for d in docs(p)]
    for d in items:
        labels = d["metadata"].get("labels", {})
        assert labels.get("app.kubernetes.io/managed-by") == OWNERSHIP, d["metadata"]["name"]
    images = []
    for d in items:
        if d["kind"] != "Deployment":
            continue
        pod = d["spec"]["template"]
        assert pod["spec"]["automountServiceAccountToken"] is False
        assert pod["spec"]["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"
        labels = pod["metadata"]["labels"]
        assert labels.get("app.kubernetes.io/managed-by") == OWNERSHIP
        for c in pod["spec"]["containers"]:
            images.append(c["image"])
            assert ":latest" not in c["image"]
            assert "@sha256:" in c["image"]
            assert c["resources"]["requests"]
            assert c["resources"]["limits"]
            assert c["readinessProbe"]["tcpSocket"]
            assert c["livenessProbe"]["tcpSocket"]
    assert any("changedetection.io:0.60.10@sha256:" in i for i in images)
    assert any("sockpuppetbrowser:0.0.3@sha256:" in i for i in images)
    app = by_kind_name(items, "Deployment", "changedetection")
    assert app["spec"]["strategy"]["type"] == "Recreate"
    env = {x["name"]: x["value"] for x in app["spec"]["template"]["spec"]["containers"][0]["env"]}
    assert env["BASE_URL"] == "https://__FQDN__"
    assert env["PLAYWRIGHT_DRIVER_URL"].startswith("ws://sockpuppet:3000/")
    ingress = by_kind_name(items, "Ingress", "changedetection")
    assert "tls" not in ingress["spec"]
    secret_pattern = re.compile(r"(?i)(password|api[_-]?key)\s*:\s*[^\s\"']+")
    assert not secret_pattern.search("\n".join(p.read_text() for p in MANIFESTS))
    print("MANIFEST_STATIC_CHECKS_PASSED")


if __name__ == "__main__":
    main()
