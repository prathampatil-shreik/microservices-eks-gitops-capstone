# ── Cluster Identity ───────────────────────────────────────────────────────────

output "cluster_name" {
  description = "EKS cluster name. Used in kubectl and Helm commands."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint URL."
  value       = module.eks.cluster_endpoint
}

output "cluster_arn" {
  description = "Full ARN of the EKS cluster."
  value       = module.eks.cluster_arn
}

output "cluster_version" {
  description = "Kubernetes version running on the cluster."
  value       = module.eks.cluster_version
}

output "aws_region" {
  description = "AWS region where the cluster is deployed."
  value       = var.aws_region
}

# ── Networking ─────────────────────────────────────────────────────────────────

output "vpc_id" {
  description = "VPC ID. Used when creating additional security groups or RDS."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs. Used for load balancers."
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs. Used for EKS nodes and RDS."
  value       = module.vpc.private_subnet_ids
}

# ── EKS Security ──────────────────────────────────────────────────────────────

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster control plane."
  value       = module.eks.cluster_security_group_id
}

output "cluster_certificate_authority_data" {
  description = "Base64-encoded certificate authority data for the cluster. Used to verify the API server TLS certificate."
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "node_security_group_id" {
  description = "Security group ID attached to EKS worker nodes."
  value       = module.eks.node_security_group_id
}

# ── IRSA / OIDC ───────────────────────────────────────────────────────────────

output "oidc_provider_arn" {
  description = "OIDC provider ARN. Required for IRSA (IAM Roles for Service Accounts)."
  value       = module.eks.oidc_provider_arn
}

output "oidc_provider_url" {
  description = "OIDC provider URL (without https://)."
  value       = module.eks.oidc_provider_url
}

# ── Load Balancer Controller ───────────────────────────────────────────────────

output "load_balancer_controller_role_arn" {
  description = "IAM role ARN for the AWS Load Balancer Controller service account."
  value       = module.load_balancer_controller.role_arn
}

output "ebs_csi_driver_role_arn" {
  description = "IAM role ARN used by the EBS CSI controller service account (IRSA)."
  value       = module.ebs_csi_driver.role_arn
}

# ── kubectl Configuration ──────────────────────────────────────────────────────

output "configure_kubectl" {
  description = "Run this command to configure kubectl to connect to the EKS cluster."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

# ── Account Info ───────────────────────────────────────────────────────────────

output "aws_account_id" {
  description = "AWS account ID where the infrastructure is deployed."
  value       = data.aws_caller_identity.current.account_id
}
