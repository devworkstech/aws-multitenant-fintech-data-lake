"""AWS Glue-compatible PySpark job for transaction curation."""
import sys
from pyspark.sql import SparkSession, functions as F, types as T

spark = SparkSession.builder.appName("curate-fintech-transactions").getOrCreate()

schema = T.StructType([
    T.StructField("tenant_id", T.StringType(), False),
    T.StructField("account_id", T.StringType(), False),
    T.StructField("event_type", T.StringType(), False),
    T.StructField("amount", T.DecimalType(18, 2), False),
    T.StructField("event_time", T.TimestampType(), False),
    T.StructField("currency", T.StringType(), True),
])


def curate(source: str, target: str) -> None:
    df = spark.read.schema(schema).json(source)
    curated = (
        df.filter(F.col("tenant_id").isNotNull())
          .filter(F.col("amount") > 0)
          .withColumn("currency", F.coalesce(F.col("currency"), F.lit("USD")))
          .withColumn("event_date", F.to_date("event_time"))
          .dropDuplicates(["tenant_id", "account_id", "event_type", "amount", "event_time"])
    )
    curated.write.mode("append").partitionBy("tenant_id", "event_date").parquet(target)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: curate_transactions.py <source> <target>")
    curate(sys.argv[1], sys.argv[2])
