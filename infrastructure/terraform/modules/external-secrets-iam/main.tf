# External Secrets Operator — IRSA
#
# IRSA pattern (same as load-balancer-controller and ebs-csi-driver modules):
#
#   1. EKS exposes an OIDC provider (created by the EKS module).
#   2. This module creates an IAM role whose trust policy restricts assumption
#      to exactly one Kubernetes service account:
#        system:serviceaccount:external-secrets:external-secrets
#   3. A least-privilege inline policy grants only the two Secrets Manager
#      actions ESO needs, scoped to the single RDS secret ARN.
#   4. The role ARN is output so it can be used to annotate the ESO service
#      account in a subsequent step (not done here).
#
# Nothing in this module touches the EKS cluster, VPC, RDS instance, or any
# other existing resource.

# ── IAM Trust Policy ──────────────────────────────────────────────────────────
# Allows only the ESO service account in the external-secrets namespace to
# assume this role via the cluster OIDC provider.
# Both conditions must be satisfied simultaneously:
#   aud = sts.amazonaws.com   — token audience check
#   sub = system:serviceaccount:external-secrets:external-secrets — SA identity
data "aws_iam_policy_document" "eso_assume_role" {
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
      values   = ["system:serviceaccount:${var.eso_namespace}:${var.eso_service_account}"]
    }
  }
}

# ── IAM Role ──────────────────────────────────────────────────────────────────
resource "aws_iam_role" "eso" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.eso_assume_role.json

  tags = {
    Name = var.role_name
  }
}

# ── Application DB Secret ─────────────────────────────────────────────────────
# Generates a strong random password and stores it in Secrets Manager as a JSON
# object with keys: username, password, database.
#
# PASSWORD SECURITY — READ CAREFULLY:
#   - The generated password is stored in plaintext inside terraform.tfstate.
#   - terraform.tfstate is excluded from Git by *.tfstate in .gitignore.
#   - terraform.tfstate.backup is excluded by *.tfstate.backup in .gitignore.
#   - Local state must be protected with Windows file-system permissions
#     (restrict to your user account only) and included in secure, encrypted
#     backups. Do NOT store local state on shared drives or in cloud sync
#     folders without encryption at rest.
#   - sensitive = true on random_password suppresses the value in plan/apply
#     terminal output but does NOT encrypt the state file.
#   - If you migrate to a remote backend (S3), enable SSE-KMS on the bucket
#     and restrict access via IAM bucket policy.
#
# override_special uses only URL-safe characters (-_.) to prevent encoding
# issues in SQLAlchemy MySQL connection URLs (mysql+pymysql://user:pass@host/).
resource "random_password" "app_db" {
  length           = 32
  special          = true
  override_special = "-_."
  min_upper        = 2
  min_lower        = 2
  min_numeric      = 2
  min_special      = 2
}

# Secret envelope — name only, no value yet.
resource "aws_secretsmanager_secret" "app_db" {
  name                    = var.app_secret_name
  description             = "Application DB credentials for microtask prod (ESO syncs this into microtask-db-secret)"
  recovery_window_in_days = 7
}

# Secret version — stores the JSON payload.
# The password value is sensitive and will not appear in plan or apply output.
resource "aws_secretsmanager_secret_version" "app_db" {
  secret_id = aws_secretsmanager_secret.app_db.id
  secret_string = jsonencode({
    username = var.app_db_username
    password = random_password.app_db.result
    database = var.app_db_name
  })
}

# ── IAM Policy ────────────────────────────────────────────────────────────────
# Two least-privilege statements — one per secret, exact ARNs, no wildcards:
#   1. AllowESOReadRDSSecret   — preserved unchanged from original implementation
#   2. AllowESOReadAppDBSecret — new, scoped to the application secret only
data "aws_iam_policy_document" "eso_secrets" {
  statement {
    sid    = "AllowESOReadRDSSecret"
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
    ]

    resources = [var.rds_secret_arn]
  }

  statement {
    sid    = "AllowESOReadAppDBSecret"
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
    ]

    resources = [aws_secretsmanager_secret.app_db.arn]
  }
}

resource "aws_iam_policy" "eso" {
  name        = "${var.role_name}-policy"
  description = "Allows ESO to read the RDS master secret from Secrets Manager"
  policy      = data.aws_iam_policy_document.eso_secrets.json
}

# ── Attachment ────────────────────────────────────────────────────────────────
resource "aws_iam_role_policy_attachment" "eso" {
  role       = aws_iam_role.eso.name
  policy_arn = aws_iam_policy.eso.arn
}
