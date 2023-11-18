from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor


default_args = {
    'owner': 'nguyenthung',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}


with DAG(
    dag_id='dag_with_minio_s3_v02',
    start_date=datetime(2023, 11, 7),
    schedule_interval='@daily',
    default_args=default_args,
    catchup =False
) as dag:
    task1 = S3KeySensor(
        task_id='sensor_minio_s3',
        bucket_name='airflow',
        bucket_key='data.csv',
        aws_conn_id='minio_conn',
        mode='poke',
        poke_interval=5,
        timeout=30
    )