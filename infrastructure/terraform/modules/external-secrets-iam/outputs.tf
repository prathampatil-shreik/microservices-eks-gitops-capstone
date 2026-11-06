output "role_arn" {
  description = "IAM role ARN for the ESO service account. Annotate the ESO service account with this ARN to activate IRSA."
  value       = aws_iam_role.eso.arn
}

output "policy_arn" {
  description = "IAM policy ARN attached to the ESO role."
  value       = aws_iam_policy.eso.arn
}

output "app_secret_arn" {
  description = "ARN of the application DB secret in Secrets Manager. Pass this to the ESO ExternalSecret resource. The secret value is never output."
  value       = aws_secretsmanager_secret.app_db.arn
}
