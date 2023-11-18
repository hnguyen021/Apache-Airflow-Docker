from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os

# Define the Python function to create a file
def create_file():
    file_path = 'home/nguyenthung/Desktop/Docker-Airflow/data/filename.txt'
    
    # Check if the directory exists, if not, create it
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Create the file
    with open(file_path, 'w') as file:
        file.write("This is a test file created by Airflow")

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG('create_file_dag',
          default_args=default_args,
          description='DAG to create a file in Ubuntu',
          schedule_interval=timedelta(days=1),
          tags=['nguyenthung'])


# Define the PythonOperator to execute the create_file function
create_file_task = PythonOperator(
    task_id='create_file_task',
    python_callable=create_file,
    dag=dag
)

create_file_task
