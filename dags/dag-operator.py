from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'nguyenthung',
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

def greet(ti):
    firstname = ti.xcom_pull(task_ids='getName', key='firstName')
    lastname = ti.xcom_pull(task_ids='getName', key='lastName')
    age = ti.xcom_pull(task_ids='getAge',key='Age')
    print(f"Hello, my name is: {firstname} {lastname}, I am {age} years old")
def getName(ti):
    ti.xcom_push(key='firstName', value='Nguyen')
    ti.xcom_push(key='lastName', value='Hung')
def getAge(ti):
    ti.xcom_push(key='Age',value=25)
with DAG(
    dag_id='dag_operator_test_v4',
    default_args=default_args,
    description='This is a first dag with operator',
    start_date=datetime(2023, 4, 11),
    schedule_interval='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='greeting',
        python_callable=greet,
        #op_kwargs={'age': 25}
    )
    task2 = PythonOperator(
        task_id='getName',
        python_callable=getName
    )
    task3 = PythonOperator(
        task_id='getAge',
        python_callable=getAge
    )



[task2,task3] >> task1
