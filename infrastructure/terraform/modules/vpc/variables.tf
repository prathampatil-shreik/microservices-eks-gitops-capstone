variable "name_prefix" {
  description = "Prefix for all resource names."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets."
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets."
  type        = list(string)
}

variable "azs" {
  description = "List of Availability Zones to use."
  type        = list(string)
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway (true) or one per AZ (false)."
  type        = bool
  default     = true
}

variable "cluster_name" {
  description = "EKS cluster name — used in subnet tags for load balancer discovery."
  type        = string
}
