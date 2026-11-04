terraform {
  required_version = ">= 1.5.0"

  required_providers {
    # AWS provider — manages all AWS resources
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.47"
    }

    # Kubernetes provider — manages K8s resources (service accounts, namespaces)
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.29"
    }

    # Helm provider — installs Helm charts (metrics-server, LBC)
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }

    # TLS provider — reads the EKS OIDC certificate thumbprint for IRSA
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }

    # HTTP provider — fetches the LBC IAM policy JSON from GitHub
    http = {
      source  = "hashicorp/http"
      version = "~> 3.4"
    }
  }
}
