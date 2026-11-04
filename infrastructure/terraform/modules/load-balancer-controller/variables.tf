variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
}

variable "aws_region" {
  description = "AWS region."
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider for IRSA."
  type        = string
}

variable "oidc_provider_url" {
  description = "URL of the EKS OIDC provider (without https://)."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID — used in the LBC Helm values."
  type        = string
}
