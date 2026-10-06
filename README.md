# AWS Multi-Tenant FinTech Data Lake

Reference implementation of a secure multi-tenant financial data lake on AWS. The project demonstrates tenant-aware ingestion, S3 lake zoning, Glue cataloging, Athena analytics, DynamoDB metadata, and infrastructure-as-code patterns appropriate for regulated financial data.

> Portfolio project using synthetic data only. It does not represent a production system or proprietary employer code.

## Architecture

```text
Synthetic banking events
        |
        v
 AWS Lambda ingestion
        |
        +----> DynamoDB tenant metadata
        |
        v
 S3 raw / tenant_id=...
        |
        v
 AWS Glue ETL + Data Catalog
        |
        v
 S3 curated / Parquet
        |
        +----> Athena / SQL analytics
        |
        +----> downstream warehouse / ML consumers
```

## Engineering focus

- Tenant isolation through partitioned S3 prefixes and explicit `tenant_id` validation.
- Idempotent event handling using deterministic event identifiers.
- Glue-compatible PySpark transformation from raw JSON to curated Parquet.
- Athena-ready partition strategy for tenant and event date pruning.
- DynamoDB metadata model for tenant configuration and ingestion state.
- Terraform examples for encrypted S3, Glue Catalog, DynamoDB and least-privilege IAM.
- Data quality checks for required fields, valid amounts and supported event types.

## Repository layout

```text
src/ingestion/handler.py       Lambda-style ingestion logic
src/etl/curate_transactions.py Glue/PySpark curation job
sql/athena_analytics.sql       Example analytical queries
terraform/main.tf              AWS infrastructure example
tests/test_ingestion.py        Unit tests
sample_data/transactions.json  Synthetic sample events
```

## Local validation

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

The Lambda handler is intentionally dependency-light so its validation logic can be tested locally. AWS calls are isolated behind a storage function to keep the core event contract easy to verify.

## Security and governance

The Terraform configuration enables S3 versioning and server-side encryption, blocks public bucket access, and scopes the example Lambda role to project resources. Production deployments should additionally use customer-managed KMS keys, VPC endpoints, centralized audit logging, Lake Formation permissions, automated PII classification, retention policies and organization-specific controls.

## Design decisions

**Why tenant + date partitions?** Financial SaaS platforms commonly need tenant isolation while retaining efficient time-window analytics. Partitioning on both dimensions allows Athena/Glue consumers to prune data without scanning unrelated tenants.

**Why raw and curated zones?** Raw immutable events preserve replayability and auditability; curated Parquet provides a stable analytical contract and lower scan cost.

**Why synthetic data?** This repository is designed as an engineering portfolio artifact and contains no customer, employer or confidential data.
