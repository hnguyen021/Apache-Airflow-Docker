from airflow import DAG
from airflow.operators.bash import BashOperator 
from datetime import datetime,timedelta


default_args ={
    'owner' : 'nguyenthung',
    'retries' : 5,
    'retry_delay' : timedelta(minutes = 2)
} 
with DAG(
    dag_id = 'first_dag_v3',
    default_args = default_args,
    description = 'this is a first dag',
    start_date = datetime(2023,3,11,2),
    schedule_interval = '@daily'
) as dag:
    task1 = BashOperator(
        task_id = 'first_task',
        bash_command = "echo helo world"

    )
    task2 = BashOperator(
        task_id = 'second_task',
        bash_command = "echo this is a task 2"
    )
    task3 = BashOperator(
        task_id = 'tgird_task',
        bash_command = "echo this is a task 3"
        )
task1 >> [task2,task3]