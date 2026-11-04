# Metrics Server
# metrics-server collects CPU and memory usage from each node's kubelet.
# Required for:
#   - kubectl top nodes
#   - kubectl top pods
#   - Horizontal Pod Autoscaler (HPA)
#   - Vertical Pod Autoscaler (VPA)

resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  version    = "3.12.2"
  namespace  = "kube-system"

  wait    = true
  timeout = 300

  # EKS node kubelets present certificates signed by the cluster CA.
  # --kubelet-insecure-tls is NOT required on EKS and is intentionally omitted.

  set {
    name  = "resources.requests.cpu"
    value = "50m"
  }

  set {
    name  = "resources.requests.memory"
    value = "64Mi"
  }

  set {
    name  = "resources.limits.cpu"
    value = "100m"
  }

  set {
    name  = "resources.limits.memory"
    value = "128Mi"
  }
}
