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


def extract():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="172.19.0.4",
        database="airflow-db",
        user="airflow",
        password="airflow",
        port='5432'
    )

    cursor = conn.cursor()

    sql = 'SELECT * from public.groceryproducts'
    csv_file_path = 'data/GroceryProducts.csv'

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
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write data to CSV file
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(data)
        print(f"Directory exists: {os.path.exists(directory)}")
        print(f"CSV file path: {csv_file_path}")
    else:
        sys.exit("No rows found for query: {}".format(sql))

    return True

def transform():
    in_csv_file_path = 'data/GroceryProducts.csv'
    out_csv_file_path = 'data/FGroceryProducts.csv'

    df = pd.read_csv(in_csv_file_path)
    df = df.head(1000)
    df["test"] = df["star_rating"] * 2

    df.to_csv(out_csv_file_path, index=False)
    return True


def email():
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import base64
    from datetime import datetime

    out_csv_file_path = 'data/FGroceryProducts.csv'

    # Set up the email components
    msg = MIMEMultipart()
    msg['From'] = 'nguyent.hung.pntv9@gmail.com'
    msg['To'] = 'nguyent.hung.f17@gmail.com'
    msg['Subject'] = 'Your file is here!'
    msg.attach(MIMEText('<img src="https://www.shb.com.vn/wp-content/uploads/2016/03/Logo-SHB-VN.png"> Dear Customer,<br>Welcome to SHB. Your file is in attachment<br>Thank you!', 'html'))

    # Attach the file
    with open(out_csv_file_path, 'rb') as f:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename='data.csv')
        msg.attach(attachment)

    # Connect to the SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('nguyent.hung.pntv9@gmail.com', 'lxug obom chnv ywbw')
        server.sendmail('nguyent.hung.pntv9@gmail.com', 'nguyent.hung.f17@gmail.com', msg.as_string())
        server.quit()
        print("Email sent successfully!")
        print(datetime.now())
    except Exception as e:
        print("Error sending email:", str(e))

    return True

dag = DAG(
    'Simple-ETL',
    default_args={
        'owner': 'nguyenthung',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A complex DAG',
    schedule=timedelta(days=1),
    start_date=datetime(2023, 11, 11),
    tags=['nguyenthung'])


extract_operator = PythonOperator(
    task_id='load_from_mysql',
    python_callable=extract,
    dag=dag
)

transform_operator = PythonOperator(
    task_id='caculate_square_amount',
    python_callable=transform,
    dag=dag
)

email_operator = PythonOperator(
    task_id='email_to_admin',
    python_callable=email,
    dag=dag
)

extract_operator >> transform_operator >> email_operator 
