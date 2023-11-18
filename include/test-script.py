
from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Simple Spark Job") \
    .getOrCreate()

# Sample data
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
columns = ["Name", "Age"]

# Create a DataFrame
df = spark.createDataFrame(data, columns)

# Perform a simple operation on the DataFrame
df.show()

# Stop the SparkSession
spark.stop()
