# EBS CSI Driver — IRSA + Managed Add-on
#
# Why this module exists as a separate root-level module rather than inside
# modules/eks:
#
#   The EKS module creates the OIDC provider. An IRSA role needs the OIDC
#   provider ARN as input. If the role were created inside the EKS module,
#   the module would depend on its own output — a cycle Terraform cannot resolve.
#
#   Solution: the EKS module exposes oidc_provider_arn and oidc_provider as
#   outputs. This module consumes those outputs AFTER the EKS module completes,
#   creating the IAM role and the addon resource in a second wave with no cycle.
#
# How IRSA works (step by step):
#
#   1. EKS creates an OIDC identity provider backed by the cluster's issuer URL.
#   2. We create an IAM role whose trust policy says:
#      "Allow the OIDC provider to call sts:AssumeRoleWithWebIdentity,
#       but ONLY for the token whose sub claim is
#       system:serviceaccount:kube-system:ebs-csi-controller-sa"
#   3. We attach AmazonEBSCSIDriverPolicy to that role.
#   4. We tell the EKS addon to use that role ARN via service_account_role_arn.
#   5. AWS injects a projected service account token into the controller pod.
#   6. The AWS SDK inside the pod exchanges that token for temporary STS
#      credentials scoped to the role — no static keys anywhere.

# ── IAM Trust Policy ──────────────────────────────────────────────────────────
# This document answers: "who is allowed to assume this role?"
# Answer: only the ebs-csi-controller-sa service account in kube-system,
# authenticated through this cluster's OIDC provider.
data "aws_iam_policy_document" "ebs_csi_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }

    actions = ["sts:AssumeRoleWithWebIdentity"]

    # aud (audience): the token must be intended for the STS service
    condition {
      test     = "StringEquals"
      variable = "${var.oidc_provider_url}:aud"
      values   = ["sts.amazonaws.com"]
    }

    # sub (subject): the token must come from this exact service account.
    # This prevents any other pod in the cluster from assuming this role.
    condition {
      test     = "StringEquals"
      variable = "${var.oidc_provider_url}:sub"
      values   = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
    }
  }
}

# ── IAM Role ──────────────────────────────────────────────────────────────────
# The role the EBS CSI controller pod will assume at runtime.
# Scoped to the minimum required: only the ebs-csi-controller-sa can use it.
resource "aws_iam_role" "ebs_csi" {
  name               = "${var.cluster_name}-ebs-csi-role"
  assume_role_policy = data.aws_iam_policy_document.ebs_csi_assume_role.json

  tags = {
    Name = "${var.cluster_name}-ebs-csi-role"
  }
}

# ── IAM Policy Attachment ─────────────────────────────────────────────────────
# AmazonEBSCSIDriverPolicy is the AWS-managed policy that grants exactly the
# permissions the EBS CSI controller needs:
#   ec2:CreateVolume, ec2:DeleteVolume, ec2:AttachVolume, ec2:DetachVolume,
#   ec2:DescribeAvailabilityZones, ec2:DescribeVolumes, etc.
# We attach the managed policy rather than writing a custom one to stay aligned
# with AWS updates to the required permission set.
resource "aws_iam_role_policy_attachment" "ebs_csi" {
  role       = aws_iam_role.ebs_csi.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

# ── EKS Managed Add-on ────────────────────────────────────────────────────────
# This resource is the AWS-managed EBS CSI driver installation.
# service_account_role_arn tells AWS to annotate the ebs-csi-controller-sa
# service account with this role ARN when it installs the addon.
# That annotation is what triggers the IRSA token injection into the pod.
#
# depends_on ensures the policy is attached before the addon is created/updated.
# Without this, the addon could start before the role has any permissions.
resource "aws_eks_addon" "this" {
  cluster_name             = var.cluster_name
  addon_name               = "aws-ebs-csi-driver"
  addon_version            = var.addon_version
  service_account_role_arn = aws_iam_role.ebs_csi.arn

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_iam_role_policy_attachment.ebs_csi]
}
