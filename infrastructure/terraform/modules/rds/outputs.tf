output "db_endpoint" {
  description = "RDS instance endpoint address (hostname only, without port)."
  value       = aws_db_instance.this.address
}

output "db_port" {
  description = "Port the RDS instance listens on."
  value       = aws_db_instance.this.port
}

output "db_name" {
  description = "Name of the database created inside the RDS instance."
  value       = aws_db_instance.this.db_name
}

output "db_identifier" {
  description = "RDS instance identifier."
  value       = aws_db_instance.this.identifier
}

output "db_secret_arn" {
  description = "ARN of the Secrets Manager secret that holds the RDS master credentials. Use this ARN to retrieve the password at runtime — never print the secret value."
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}

output "rds_security_group_id" {
  description = "ID of the security group attached to the RDS instance."
  value       = aws_security_group.rds.id
}
