from datetime import datetime, timedelta
import csv
import sys
import os
from airflow import DAG
import pandas as pd
from airflow.operators.python import PythonOperator
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import getpass


default_args = {
    'owner': 'nguyenthung',
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

def CreateFile():
    print("Current Working Directory:", os.getcwd())
    print("User Running Process:", getpass.getuser())
    print("Environment Variables:", os.environ)
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="172.19.0.2",
        database="airflow-db",
        user="airflow",
        password="airflow",
        port='5432'
    )

    cursor = conn.cursor()

    sql = 'SELECT * from public.groceryproducts'
    csv_file_path = '/home/nguyenthung/Desktop/Docker-Airflow/data/GroceryProducts.csv'

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    # Continue only if there are rows returned.
    if rows:
        # Get column names
        column_names = [desc[0] for desc in cursor.description]

        # Create a list to hold the data (including column names)
        data = [column_names] + list(rows)

        # Ensure the directory exists, create if not
        directory = os.path.dirname(csv_file_path)
        print(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
            print("LOL")

        # Write data to CSV file
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(data)
        print(f"Directory exists: {os.path.exists(directory)}")
        print(f"CSV file path: {csv_file_path}")
    else:
        sys.exit("No rows found for query: {}".format(sql))

 
with DAG(
    dag_id='CreateFile',
    default_args=default_args,
    description='CreateFile',
    start_date=datetime(2023,11,11),
    schedule_interval='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='CreateFile',
        python_callable=CreateFile,
    )
task1
   



