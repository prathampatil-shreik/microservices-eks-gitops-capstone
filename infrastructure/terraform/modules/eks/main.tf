# EKS Module
# Uses the official terraform-aws-modules/eks/aws module.
# Creates:
#   - EKS control plane
#   - Managed node group (worker nodes in private subnets)
#   - IAM roles for cluster and nodes
#   - OIDC provider for IRSA
#   - EKS managed add-ons: vpc-cni, coredns, kube-proxy
#   - aws-ebs-csi-driver is managed separately in modules/ebs-csi-driver
#     to avoid a dependency cycle between the OIDC provider and the addon's IRSA role.

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.11"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  # ── Networking ──────────────────────────────────────────────────────────────
  # The control plane ENIs are placed in both public and private subnets.
  # Worker nodes only go into private subnets (configured in node group below).
  vpc_id     = var.vpc_id
  subnet_ids = concat(var.private_subnet_ids, var.public_subnet_ids)

  # ── API Server Access ────────────────────────────────────────────────────────
  # Public endpoint: allows kubectl from your laptop
  # Private endpoint: allows nodes to reach the API server inside the VPC
  # Both enabled is the standard setup for EKS
  cluster_endpoint_public_access       = true
  cluster_endpoint_private_access      = true
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs

  # ── OIDC Provider ────────────────────────────────────────────────────────────
  # Required for IRSA (IAM Roles for Service Accounts).
  # IRSA lets Kubernetes pods assume IAM roles without storing credentials.
  # Used by: AWS Load Balancer Controller, External Secrets Operator, etc.
  enable_irsa = true

  # ── Control Plane Logging ────────────────────────────────────────────────────
  # Logs are sent to CloudWatch Logs.
  # api:               API server audit logs
  # audit:             who did what to the cluster
  # authenticator:     IAM authentication events
  # controllerManager: controller decisions
  # scheduler:         pod scheduling decisions
  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  # ── EKS Managed Add-ons ──────────────────────────────────────────────────────
  # These are AWS-managed versions of core Kubernetes components.
  # AWS handles patching and updates for these add-ons.
  cluster_addons = {
    # vpc-cni: assigns VPC IP addresses to pods (AWS-native pod networking)
    vpc-cni = {
      most_recent = true
    }
    # coredns: cluster DNS — resolves service names like "mysql.microtask.svc.cluster.local"
    coredns = {
      most_recent = true
    }
    # kube-proxy: maintains network rules on each node for Service routing
    kube-proxy = {
      most_recent = true
    }
  }

  # ── Managed Node Group ───────────────────────────────────────────────────────
  # Managed node groups: AWS handles node provisioning, patching, and replacement.
  # Nodes run in private subnets — they are NOT directly reachable from the internet.
  eks_managed_node_groups = {
    microtask-workers = {
      name = "microtask-workers"

      # Only place nodes in private subnets
      subnet_ids = var.private_subnet_ids

      instance_types = [var.node_instance_type]
      disk_size      = var.node_disk_size

      min_size     = var.node_min_size
      max_size     = var.node_max_size
      desired_size = var.node_desired_size

      # AL2023 is the required AMI for Kubernetes 1.32 and above.
      # AL2 (Amazon Linux 2) reached end of standard support for EKS >= 1.32.
      ami_type = "AL2023_x86_64_STANDARD"

      # Labels applied to every node — useful for node selectors in Helm charts
      labels = {
        role        = "worker"
        environment = var.name_prefix
      }
    }
  }

  # ── Access Entries ───────────────────────────────────────────────────────────
  # Grants the IAM principal running Terraform cluster-admin access.
  # Without this, even the creator cannot run kubectl commands.
  enable_cluster_creator_admin_permissions = true
}
