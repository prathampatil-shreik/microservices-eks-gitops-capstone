variable "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider. Used as the federated principal in the trust policy."
  type        = string
}

variable "oidc_provider_url" {
  description = "URL of the EKS OIDC provider without https://. Used as the condition key prefix in the trust policy."
  type        = string
}

variable "role_name" {
  description = "Name of the IAM role created for ESO."
  type        = string
  default     = "microtask-eks-dev-external-secrets-role"
}

variable "rds_secret_arn" {
  description = "Exact ARN of the RDS-managed master secret ESO is permitted to read. No wildcard — least-privilege."
  type        = string
}

variable "eso_namespace" {
  description = "Kubernetes namespace where the ESO service account lives."
  type        = string
  default     = "external-secrets"
}

variable "eso_service_account" {
  description = "Kubernetes service account name used by ESO."
  type        = string
  default     = "external-secrets"
}

variable "app_secret_name" {
  description = "Secrets Manager secret name for the application DB credentials. Uses path-style naming for logical grouping."
  type        = string
  default     = "microtask/prod/database"
}

variable "app_db_username" {
  description = "Application database username stored in the app secret. This user must be created inside MySQL separately after apply."
  type        = string
  default     = "microtask_app"
}

variable "app_db_name" {
  description = "Database name stored in the app secret."
  type        = string
  default     = "microtask_db"
}
