# VPC Module
# Uses the official terraform-aws-modules/vpc/aws module.
# This module creates everything needed for a production-style VPC:
#   - VPC with DNS support
#   - Public subnets (for load balancers)
#   - Private subnets (for EKS nodes)
#   - Internet Gateway (public subnet outbound)
#   - NAT Gateway (private subnet outbound)
#   - Route tables and associations
#   - Subnet tags required by Kubernetes for load balancer discovery

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "${var.name_prefix}-vpc"
  cidr = var.vpc_cidr

  # Deploy subnets across two AZs for high availability
  azs             = var.azs
  public_subnets  = var.public_subnet_cidrs
  private_subnets = var.private_subnet_cidrs

  # ── Internet Gateway ──────────────────────────────────────────────────────
  # Allows public subnets to reach the internet directly.
  # Required for: load balancers, bastion hosts, NAT Gateway itself.
  create_igw = true

  # ── NAT Gateway ───────────────────────────────────────────────────────────
  # Allows private subnet resources (EKS nodes) to reach the internet
  # for pulling container images, calling AWS APIs, etc.
  # Nodes cannot be reached FROM the internet through NAT.
  enable_nat_gateway = true

  # single_nat_gateway = true:  one NAT Gateway in the first AZ
  #   Cost: ~$32/month + $0.045/GB data processed
  #   Risk: if that AZ goes down, all private subnets lose internet access
  #   Use for: dev, learning, cost-sensitive environments
  #
  # single_nat_gateway = false: one NAT Gateway per AZ
  #   Cost: ~$64/month + data transfer
  #   Benefit: full HA — AZ failure only affects that AZ's nodes
  #   Use for: production workloads
  single_nat_gateway = var.single_nat_gateway

  # ── DNS ───────────────────────────────────────────────────────────────────
  # Both must be true for EKS to work correctly.
  # enable_dns_hostnames: EC2 instances get DNS names
  # enable_dns_support:   VPC DNS resolver is active
  enable_dns_hostnames = true
  enable_dns_support   = true

  # ── Kubernetes Subnet Tags ────────────────────────────────────────────────
  # These tags tell the AWS Load Balancer Controller which subnets to use.
  # Without these tags, the controller cannot discover subnets automatically.
  #
  # Public subnets: internet-facing load balancers (ALB/NLB)
  public_subnet_tags = {
    "kubernetes.io/role/elb"                    = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }

  # Private subnets: internal load balancers + EKS nodes
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"           = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}
