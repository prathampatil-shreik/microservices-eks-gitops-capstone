# ── AWS Provider ──────────────────────────────────────────────────────────────
# Reads credentials from the AWS CLI profile configured on your machine.
# Never hardcode access keys here.
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

# ── Kubernetes Provider ────────────────────────────────────────────────────────
# Configured dynamically after EKS is created.
# Uses the cluster endpoint and CA certificate from the EKS module output.
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks", "get-token",
      "--cluster-name", module.eks.cluster_name,
      "--region", var.aws_region
    ]
  }
}

# ── Helm Provider ──────────────────────────────────────────────────────────────
# Same authentication as the Kubernetes provider.
# Used to install metrics-server and AWS Load Balancer Controller.
provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks", "get-token",
        "--cluster-name", module.eks.cluster_name,
        "--region", var.aws_region
      ]
    }
  }
}
