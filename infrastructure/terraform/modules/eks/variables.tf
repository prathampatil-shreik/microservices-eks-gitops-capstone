variable "name_prefix" {
  description = "Prefix for resource names and labels."
  type        = string
}

variable "cluster_name" {
  description = "Name of the EKS cluster."
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version for the EKS cluster."
  type        = string
}

variable "aws_region" {
  description = "AWS region."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the cluster is deployed."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for worker nodes."
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for the control plane ENIs."
  type        = list(string)
}

variable "node_instance_type" {
  description = "EC2 instance type for worker nodes."
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
  description = "EBS root volume size in GB per node."
  type        = number
  default     = 20
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDR blocks allowed to reach the EKS public API endpoint. Must be set explicitly — no default."
  type        = list(string)
}
