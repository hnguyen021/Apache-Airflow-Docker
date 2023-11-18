from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os

def change_working_directory():
    new_directory = '/home/nguyenthung/Desktop/Docker-Airflow'

    # Change the current working directory
    os.chdir(new_directory)

    # Check if the directory has been changed
    print(f"Current Working Directory: {os.getcwd()}")


dag = DAG(
    'change_working_dir_example',
    default_args={
        'owner': 'nguyenthung',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A complex DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 11, 11),
    tags=['nguyenthung'])

change_dir_task = PythonOperator(
    task_id='change_working_directory_task',
    python_callable=change_working_directory,
    dag=dag
)
