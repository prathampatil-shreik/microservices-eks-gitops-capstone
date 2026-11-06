variable "name_prefix" {
  description = "Prefix for all resource names. Matches the root local.name_prefix convention."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the RDS instance and security group are created."
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the DB subnet group. Must span at least two AZs."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "At least two private subnet IDs in different Availability Zones are required for the DB subnet group."
  }
}

variable "eks_node_security_group_id" {
  description = "Security group ID of the EKS worker nodes. Only this SG is allowed to reach MySQL on port 3306."
  type        = string
}

variable "db_identifier" {
  description = "Unique identifier for the RDS instance."
  type        = string
  default     = "microtask-prod-mysql"
}

variable "db_name" {
  description = "Name of the initial database created inside the RDS instance."
  type        = string
  default     = "microtask_db"
}

variable "db_username" {
  description = "Master username for the RDS instance."
  type        = string
  default     = "microtask_admin"
}

variable "db_port" {
  description = "TCP port MySQL listens on."
  type        = number
  default     = 3306
}

variable "engine_version" {
  description = "MySQL engine version. 8.0.46 is the latest available in us-east-1 and is compatible with db.t3.micro."
  type        = string
  default     = "8.0.46"
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Initial storage allocation in GB."
  type        = number
  default     = 20
}

variable "storage_type" {
  description = "EBS storage type for the RDS instance."
  type        = string
  default     = "gp3"
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups. Free Tier maximum is 1."
  type        = number
  default     = 1
}

variable "backup_window" {
  description = "Daily UTC time window for automated backups (hh24:mi-hh24:mi)."
  type        = string
  default     = "03:00-04:00"
}
