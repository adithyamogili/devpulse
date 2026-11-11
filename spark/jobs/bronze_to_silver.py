from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("DevPulseBronzeToSilver").getOrCreate()
jdbc = "jdbc:postgresql://postgres:5432/devpulse"
props = {"user":"devpulse", "password":"devpulse", "driver":"org.postgresql.Driver"}
source = spark.read.jdbc(jdbc, "bronze.github_api_records", properties=props)

payload = source.select(
    "repository_full_name", "resource_type", "record_id", "payload",
    F.coalesce(F.get_json_object(F.col("payload").cast("string"), "$.user.login"),
               F.get_json_object(F.col("payload").cast("string"), "$.author.login")).alias("author_login"),
    F.to_timestamp(F.coalesce(
        F.get_json_object(F.col("payload").cast("string"), "$.created_at"),
        F.get_json_object(F.col("payload").cast("string"), "$.commit.author.date")
    )).alias("created_at"),
    F.to_timestamp(F.get_json_object(F.col("payload").cast("string"), "$.updated_at")).alias("updated_at"),
    F.get_json_object(F.col("payload").cast("string"), "$.state").alias("state"),
    F.get_json_object(F.col("payload").cast("string"), "$.title").alias("title"),
)
enriched = payload.withColumn("event_date", F.to_date("created_at")).withColumn("processed_at", F.current_timestamp())
enriched.write.jdbc(jdbc, "silver.github_activity_enriched", mode="overwrite", properties=props)
spark.stop()
