# RDS Module — Production MySQL
#
# Architecture decisions:
#
# 1. SECURITY GROUP
#    A dedicated SG is created for RDS. The only inbound rule allows TCP 3306
#    from the EKS worker-node SG. No public access, no 0.0.0.0/0.
#    The EKS worker-node SG is NOT modified — we reference it as a source only.
#
# 2. DB SUBNET GROUP
#    Uses the existing VPC private subnets (same subnets as EKS nodes).
#    Requires at least two subnets in different AZs (AWS requirement).
#
# 3. CREDENTIALS
#    manage_master_user_password = true delegates password generation to
#    Amazon RDS + Secrets Manager. No password is ever stored in Terraform
#    state, variables, or outputs. The secret ARN is the only
#    credential-related output. Automatic rotation is NOT configured; to
#    enable rotation, add an aws_secretsmanager_secret_rotation resource.
#
# 4. ENCRYPTION
#    storage_encrypted = true encrypts the EBS volume at rest using the
#    AWS-managed RDS KMS key (no extra cost, no key management overhead).
#
# 5. DELETION PROTECTION
#    deletion_protection = true prevents accidental destruction via the AWS
#    console or CLI. To delete the instance, this must be set to false first
#    and applied, then destroy can proceed.

# ── RDS Security Group ────────────────────────────────────────────────────────
# Dedicated security group for the RDS instance.
# Only the EKS worker-node security group can reach port 3306.
resource "aws_security_group" "rds" {
  name        = "microtask-prod-rds-sg"
  description = "Allow MySQL access to production RDS from EKS worker nodes only"
  vpc_id      = var.vpc_id

  tags = {
    Name        = "microtask-prod-rds-sg"
    Environment = "prod"
  }
}

# Inbound: MySQL from EKS worker nodes only.
# Using a separate rule resource (not inline) keeps the SG definition stable
# and avoids the known Terraform cycle issue with inline ingress/egress blocks.
resource "aws_vpc_security_group_ingress_rule" "rds_from_eks_nodes" {
  security_group_id            = aws_security_group.rds.id
  description                  = "MySQL from EKS worker nodes to production RDS"
  from_port                    = var.db_port
  to_port                      = var.db_port
  ip_protocol                  = "tcp"
  referenced_security_group_id = var.eks_node_security_group_id

  tags = {
    Name        = "microtask-prod-rds-ingress-mysql"
    Environment = "prod"
  }
}

# Outbound: no egress rules are defined. AWS security groups are default-deny
# for outbound when no egress rules exist, which is the correct restrictive
# configuration for RDS — it only needs to respond to inbound connections.

# ── DB Subnet Group ───────────────────────────────────────────────────────────
# AWS requires a subnet group spanning at least two AZs for RDS, even for
# Single-AZ deployments. The instance is placed in one AZ; the second subnet
# is required by the API but unused unless you enable Multi-AZ later.
resource "aws_db_subnet_group" "this" {
  name        = "microtask-prod-rds-subnet-group"
  description = "Private subnets for production RDS instance"
  subnet_ids  = var.private_subnet_ids

  tags = {
    Name        = "microtask-prod-rds-subnet-group"
    Environment = "prod"
  }
}

# ── RDS Instance ──────────────────────────────────────────────────────────────
resource "aws_db_instance" "this" {
  identifier = var.db_identifier

  # Engine
  engine         = "mysql"
  engine_version = var.engine_version
  instance_class = var.instance_class

  # Storage
  allocated_storage = var.allocated_storage
  storage_type      = var.storage_type
  storage_encrypted = true

  # Database
  db_name  = var.db_name
  username = var.db_username
  port     = var.db_port

  # Credentials — RDS generates and stores the password in Secrets Manager.
  # No password is ever written to Terraform state or variables.
  manage_master_user_password = true

  # Networking — private only, no public endpoint
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # Availability — Single-AZ for cost efficiency
  multi_az = false

  # Backups
  backup_retention_period = var.backup_retention_period
  backup_window           = var.backup_window

  # Maintenance
  auto_minor_version_upgrade = true

  # Observability — disabled to keep costs minimal
  performance_insights_enabled = false
  monitoring_interval          = 0

  # Safety — prevents accidental deletion.
  # To destroy this instance: set deletion_protection = false, apply, then destroy.
  deletion_protection = true

  # Final snapshot — taken automatically before the instance is deleted.
  # Provides a last-resort backup even when deletion_protection is disabled.
  skip_final_snapshot       = false
  final_snapshot_identifier = "microtask-prod-mysql-final"

  # Copy all instance tags to automated backups and the final snapshot.
  copy_tags_to_snapshot = true

  tags = {
    Name        = var.db_identifier
    Environment = "prod"
  }
}
