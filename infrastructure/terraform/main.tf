# ── VPC Module ────────────────────────────────────────────────────────────────
# Creates the VPC, subnets, IGW, NAT Gateway, and route tables.
# Everything EKS needs to run in a proper network.
module "vpc" {
  source = "./modules/vpc"

  name_prefix          = local.name_prefix
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  azs                  = local.azs
  single_nat_gateway   = var.single_nat_gateway
  cluster_name         = var.cluster_name
}

# ── EKS Module ────────────────────────────────────────────────────────────────
# Creates the EKS cluster, managed node group, IAM roles, and add-ons.
# Worker nodes are placed in the private subnets from the VPC module.
module "eks" {
  source = "./modules/eks"

  name_prefix        = local.name_prefix
  cluster_name       = var.cluster_name
  kubernetes_version = var.kubernetes_version
  aws_region         = var.aws_region

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids

  node_instance_type = var.node_instance_type
  node_desired_size  = var.node_desired_size
  node_min_size      = var.node_min_size
  node_max_size      = var.node_max_size
  node_disk_size     = var.node_disk_size

  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
}

# ── AWS Load Balancer Controller Module ───────────────────────────────────────
# Creates the IAM role and service account for the AWS Load Balancer Controller.
# The actual Helm chart installation is documented in the README.
# This module only provisions the IAM prerequisites (IRSA pattern).
module "load_balancer_controller" {
  source = "./modules/load-balancer-controller"

  cluster_name      = var.cluster_name
  aws_region        = var.aws_region
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url
  vpc_id            = module.vpc.vpc_id

  depends_on = [module.eks]
}

# ── Metrics Server Module ─────────────────────────────────────────────────────
# Installs metrics-server into the EKS cluster via Helm.
# Required for: kubectl top nodes, kubectl top pods, HPA.
module "metrics_server" {
  source = "./modules/metrics-server"

  depends_on = [module.eks]
}

# ── EBS CSI Driver Module ─────────────────────────────────────────────────────
# Creates the IRSA role and manages the aws-ebs-csi-driver EKS addon.
#
# This is intentionally a root-level module rather than part of modules/eks.
# Reason: the IRSA role needs module.eks.oidc_provider_arn as input, but the
# EKS module itself creates the OIDC provider. Putting the role inside the EKS
# module would create a self-referential dependency cycle.
#
# By placing it here, Terraform resolves the graph correctly:
#   module.vpc → module.eks (creates OIDC) → module.ebs_csi_driver (uses OIDC)
module "ebs_csi_driver" {
  source = "./modules/ebs-csi-driver"

  cluster_name      = var.cluster_name
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url

  depends_on = [module.eks]
}

# ── RDS Module ─────────────────────────────────────────────────────────────────
# Provisions a production MySQL 8.0 RDS instance in the existing VPC.
# - Placed in private subnets (same as EKS nodes, no public access).
# - Dedicated security group allows port 3306 from EKS worker nodes only.
# - Master password managed by Amazon RDS + Secrets Manager (no plaintext).
# - Single-AZ, db.t3.micro for cost efficiency in this capstone environment.
# - Deletion protection enabled; must be disabled before terraform destroy.
module "rds" {
  source = "./modules/rds"

  name_prefix                = local.name_prefix
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  eks_node_security_group_id = module.eks.node_security_group_id

  depends_on = [module.vpc]
}

# ── External Secrets Operator — IRSA ──────────────────────────────────────────
# Creates the IAM role and least-privilege policy that allow the ESO service
# account (external-secrets/external-secrets) to call GetSecretValue and
# DescribeSecret on the RDS master secret only.
#
# OIDC values come from the existing EKS module outputs — nothing is hardcoded.
# The RDS secret ARN comes from the existing RDS module output.
#
# This module does NOT annotate the service account. That step is intentionally
# deferred so the role ARN can be reviewed before it is applied.
module "external_secrets_iam" {
  source = "./modules/external-secrets-iam"

  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url
  rds_secret_arn    = module.rds.db_secret_arn

  depends_on = [module.eks, module.rds]
}
