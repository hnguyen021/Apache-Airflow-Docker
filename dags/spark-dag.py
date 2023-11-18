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
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args={
        'owner': 'nguyenthung',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
with DAG(
    dag_id='dag_spark_operator',
    default_args=default_args,
    description='This is a spark operator',
    start_date=datetime(2023, 4, 11),
    schedule_interval='@daily'
) as dag:
    task1 = SparkSubmitOperator(
        task_id='submit_job',
        application = 'test-script.py',
        conn_id = 'spark_default',
        total_executor_cores = '1',
        executor_cores = '1',
        executor_memory = '2g',
        num_executors = '1',
        driver_memory = '2g',
        verbose = False
        #op_kwargs={'age': 25}
    )
task1
