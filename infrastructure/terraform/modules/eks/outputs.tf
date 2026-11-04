output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint."
  value       = module.eks.cluster_endpoint
}

output "cluster_arn" {
  description = "EKS cluster ARN."
  value       = module.eks.cluster_arn
}

output "cluster_version" {
  description = "Kubernetes version of the cluster."
  value       = module.eks.cluster_version
}

output "cluster_certificate_authority_data" {
  description = "Base64-encoded CA certificate for the cluster."
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_security_group_id" {
  description = "Security group ID for the EKS control plane."
  value       = module.eks.cluster_security_group_id
}

output "node_security_group_id" {
  description = "Security group ID for the EKS worker nodes."
  value       = module.eks.node_security_group_id
}

output "oidc_provider_arn" {
  description = "ARN of the OIDC provider — required for IRSA."
  value       = module.eks.oidc_provider_arn
}

output "oidc_provider_url" {
  description = "URL of the OIDC provider (without https://)."
  value       = module.eks.oidc_provider
}
