terraform {
  required_version = ">= 1.5.0"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}

provider "aws" { region = var.aws_region }

variable "aws_region" { type = string; default = "us-east-1" }
variable "project_name" { type = string; default = "fintech-multitenant-lake" }

resource "aws_s3_bucket" "lake" { bucket_prefix = "${var.project_name}-" }
resource "aws_s3_bucket_public_access_block" "lake" {
  bucket = aws_s3_bucket.lake.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_versioning" "lake" {
  bucket = aws_s3_bucket.lake.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "lake" {
  bucket = aws_s3_bucket.lake.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "AES256" } }
}

resource "aws_glue_catalog_database" "lake" { name = replace(var.project_name, "-", "_") }

resource "aws_dynamodb_table" "tenant_metadata" {
  name         = "${var.project_name}-tenant-metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "tenant_id"
  attribute { name = "tenant_id"; type = "S" }
  point_in_time_recovery { enabled = true }
  server_side_encryption { enabled = true }
}

output "lake_bucket" { value = aws_s3_bucket.lake.id }
output "glue_database" { value = aws_glue_catalog_database.lake.name }
