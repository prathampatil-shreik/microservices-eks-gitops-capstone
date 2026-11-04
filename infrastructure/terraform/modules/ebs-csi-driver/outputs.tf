output "role_arn" {
  description = "IAM role ARN used by the EBS CSI controller service account."
  value       = aws_iam_role.ebs_csi.arn
}
