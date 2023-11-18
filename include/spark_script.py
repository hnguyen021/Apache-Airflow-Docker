from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder \
    .appName("Read from PostgreSQL") \
    .config("spark.jars", "resources/postgresql-42.6.0.jar") \
    .getOrCreate()

# PostgreSQL connection properties
db_properties = {
    "driver": "org.postgresql.Driver",
    "url": "jdbc:postgresql://localhost:5432/airflow-db",
    "user": "airflow",
    "password": "airflow",
    "dbtable": "groceryproducts"
}

# Read data from PostgreSQL using JDBC
df = spark.read \
    .format("jdbc") \
    .option("driver", db_properties['driver']) \
    .option("url", db_properties['url']) \
    .option("dbtable", db_properties['dbtable']) \
    .option("user", db_properties['user']) \
    .option("password", db_properties['password']) \
    .load()

# Show the data
df.show()
