output "role_arn" {
  description = "IAM role ARN for the AWS Load Balancer Controller service account."
  value       = aws_iam_role.lbc.arn
}

output "policy_arn" {
  description = "IAM policy ARN attached to the LBC role."
  value       = aws_iam_policy.lbc.arn
}

output "service_account_name" {
  description = "Kubernetes service account name for the LBC."
  value       = kubernetes_service_account.lbc.metadata[0].name
}
