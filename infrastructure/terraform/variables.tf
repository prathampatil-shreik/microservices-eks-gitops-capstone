# ── Project ────────────────────────────────────────────────────────────────────

variable "project_name" {
  description = "Short project identifier used in resource names and tags."
  type        = string
  default     = "microtask"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)."
  type        = string
  default     = "dev"
}

# ── AWS ────────────────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region where all resources are created."
  type        = string
  default     = "us-east-1"
}

# ── Networking ─────────────────────────────────────────────────────────────────

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per AZ)."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets (one per AZ). EKS nodes run here."
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "single_nat_gateway" {
  description = <<-EOT
    When true: one NAT Gateway shared across all private subnets.
      Cost: ~$32/month + data transfer. Good for dev/learning.
    When false: one NAT Gateway per AZ.
      Cost: ~$64/month + data transfer. Required for production HA.
  EOT
  type        = bool
  default     = true
}

# ── EKS ────────────────────────────────────────────────────────────────────────

variable "cluster_name" {
  description = "Name of the EKS cluster."
  type        = string
  default     = "microtask-eks-dev"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the EKS cluster. Check AWS docs for supported versions."
  type        = string
  default     = "1.36"
}

variable "node_instance_type" {
  description = <<-EOT
    EC2 instance type for EKS worker nodes.
    t3.medium (2 vCPU, 4GB RAM) — ~$30/month per node. Good for learning.
    t3.large  (2 vCPU, 8GB RAM) — ~$60/month per node. Better for production.
  EOT
  type        = string
  default     = "t3.medium"
}

variable "node_desired_size" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 2
}

variable "node_disk_size" {
  description = "EBS root volume size in GB for each worker node."
  type        = number
  default     = 20
}

# ── EKS Access ─────────────────────────────────────────────────────────────────

variable "cluster_endpoint_public_access_cidrs" {
  description = <<-EOT
    List of CIDR blocks allowed to reach the EKS public API endpoint.
    Must be set explicitly in terraform.tfvars — there is no default.
    Find your public IP: curl https://checkip.amazonaws.com
    Example: ["203.0.113.42/32"]
  EOT
  type        = list(string)

  validation {
    condition     = length(var.cluster_endpoint_public_access_cidrs) > 0
    error_message = "cluster_endpoint_public_access_cidrs must contain at least one CIDR. Set it in terraform.tfvars (e.g. [\"YOUR_IP/32\"])."
  }
}
