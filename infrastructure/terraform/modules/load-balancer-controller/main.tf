# AWS Load Balancer Controller — IAM Prerequisites
#
# The AWS Load Balancer Controller is a Kubernetes controller that:
#   - Creates ALBs for Kubernetes Ingress resources
#   - Creates NLBs for LoadBalancer-type Services
#
# IRSA (IAM Roles for Service Accounts) pattern:
#   1. EKS creates an OIDC provider (done in EKS module)
#   2. We create an IAM role that trusts that OIDC provider
#   3. We annotate the Kubernetes service account with the role ARN
#   4. When the controller pod starts, it automatically gets AWS credentials
#      via the projected service account token — no secrets needed
#
# This module only creates the IAM prerequisites.
# The actual Helm chart is installed separately (see README).

# ── IAM Policy ────────────────────────────────────────────────────────────────
# The official AWS-provided policy for the Load Balancer Controller.
# v2.13.x is the current release line compatible with Kubernetes 1.29–1.36.
data "http" "lbc_iam_policy" {
  url = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.13.1/docs/install/iam_policy.json"
}

resource "aws_iam_policy" "lbc" {
  name        = "${var.cluster_name}-lbc-policy"
  description = "IAM policy for AWS Load Balancer Controller on cluster ${var.cluster_name}"
  policy      = data.http.lbc_iam_policy.response_body
}

# ── IAM Role (IRSA) ───────────────────────────────────────────────────────────
# This role can only be assumed by the specific Kubernetes service account
# in the kube-system namespace of this specific EKS cluster.
# The trust policy uses the OIDC provider to verify the service account identity.
data "aws_iam_policy_document" "lbc_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }

    actions = ["sts:AssumeRoleWithWebIdentity"]

    condition {
      test     = "StringEquals"
      variable = "${var.oidc_provider_url}:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "${var.oidc_provider_url}:sub"
      values   = ["system:serviceaccount:kube-system:aws-load-balancer-controller"]
    }
  }
}

resource "aws_iam_role" "lbc" {
  name               = "${var.cluster_name}-lbc-role"
  assume_role_policy = data.aws_iam_policy_document.lbc_assume_role.json

  tags = {
    Name = "${var.cluster_name}-lbc-role"
  }
}

resource "aws_iam_role_policy_attachment" "lbc" {
  role       = aws_iam_role.lbc.name
  policy_arn = aws_iam_policy.lbc.arn
}

# ── Kubernetes Service Account ────────────────────────────────────────────────
# The annotation links this service account to the IAM role above.
# When the controller pod uses this service account, it gets the IAM role's permissions.
resource "kubernetes_service_account" "lbc" {
  metadata {
    name      = "aws-load-balancer-controller"
    namespace = "kube-system"

    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.lbc.arn
    }

    labels = {
      "app.kubernetes.io/name"      = "aws-load-balancer-controller"
      "app.kubernetes.io/component" = "controller"
    }
  }
}
