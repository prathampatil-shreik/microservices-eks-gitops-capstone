variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider. Used in the IAM role trust policy."
  type        = string
}

variable "oidc_provider_url" {
  description = "URL of the EKS OIDC provider without https://. Used as the condition key in the trust policy."
  type        = string
}

variable "addon_version" {
  description = "EBS CSI driver addon version. Use 'most_recent' equivalent by pinning to a known-good version."
  type        = string
  default     = "v1.67.2-eksbuild.1"
}
