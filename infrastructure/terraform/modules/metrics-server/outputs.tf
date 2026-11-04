output "helm_release_status" {
  description = "Status of the metrics-server Helm release."
  value       = helm_release.metrics_server.status
}
