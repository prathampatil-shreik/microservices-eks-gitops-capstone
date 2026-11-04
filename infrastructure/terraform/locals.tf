# Locals are computed values derived from variables.
# Defining them here avoids repeating the same expressions in every module.

locals {
  # Name prefix used in every resource name for easy identification
  name_prefix = "${var.project_name}-${var.environment}"

  # Common tags applied to every AWS resource via the provider default_tags block.
  # This means you never forget to tag a resource.
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Repository  = "microservices-eks-gitops-capstone"
  }

  # Dynamically fetch the first two AZs in the selected region.
  # This avoids hardcoding AZ names like "us-east-1a" which can vary.
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# Data source: fetch available AZs in the configured region
data "aws_availability_zones" "available" {
  state = "available"
  # Exclude Local Zones which don't support all EKS features
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

# Data source: current AWS account ID and caller identity
# Used in IAM policies and outputs without hardcoding account IDs
data "aws_caller_identity" "current" {}
