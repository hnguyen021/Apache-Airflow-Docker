from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from datetime import date
import json
import time
import sys
from airflow import DAG
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from airflow.operators.python import PythonOperator
import numpy as np
import ssl
from datetime import datetime, timedelta
import csv
from psycopg2 import connect, extras
import os
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass



ssl._create_default_https_context = ssl._create_unverified_context
def craw_stock_price(**kwargs):
    print("Current Working Directory:", os.getcwd())
    print("User Running Process:", getpass.getuser())
    print("Environment Variables:", os.environ)

    to_date = kwargs["to_date"]
    from_date = "2000-01-01"

    stock_price_df = pd.DataFrame()
    stock_code = "DIG"
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

    url = "https://finfo-api.vndirect.com.vn/v4/stock_prices?sort=date&q=code:{}~date:gte:{}~date:lte:{}&size=9990&page=1".format(stock_code, from_date, to_date)
    # url = "https://github.com/thangnch/MiAI_Stock_Predict/raw/master/stock_prices.json"
    print(url)


    from urllib.request import Request, urlopen

    req = Request(url, headers={'User-Agent': 'Mozilla / 5.0 (Windows NT 6.1; WOW64; rv: 12.0) Gecko / 20100101 Firefox / 12.0'})
    x = urlopen(req, timeout=10).read()

    req.add_header("Authorization", "Basic %s" % "ABCZYXX")

    json_x = json.loads(x)['data']

    for stock in json_x:

        #stock_price_df = stock_price_df.append(stock, ignore_index=True)
        stock_price_df = pd.concat([stock_price_df, pd.DataFrame([stock])], ignore_index=True)

    print(stock_price_df.head(5))
    print("Header của DataFrame:")
    print(stock_price_df.columns.tolist())  # hoặc print(list(df.columns))
    print("\nKiểu dữ liệu của các cột trong DataFrame:")
    print(stock_price_df.dtypes)
    csv_file_path = "data/stock_price.csv"
    # directory = os.path.dirname(csv_file_path)
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    stock_price_df.to_csv(csv_file_path, index=None)

    return True

def transform():
    in_csv_file_path = 'data/stock_price.csv'
    out_csv_file_path = 'data/stock_price.csv'

    df = pd.read_csv(in_csv_file_path)
    df.columns = df.columns.str.strip()

    missing_values = df.isnull().sum()
    # Xử lý giá trị thiếu nếu cần thiết

    # Điều chỉnh định dạng số (ví dụ: loại bỏ dấu phẩy trong các cột số)
    numeric_columns = ['basicPrice', 'ceilingPrice', 'floorPrice','open', 'high', 'low', 'close','average', 'adOpen', 'adHigh', 'adLow', 'adClose', 'adAverage', 'nmVolume', 'nmValue', 'ptVolume', 'ptValue','change', 'adChange', 'pctChange']  # Danh sách các cột số
    df[numeric_columns] = df[numeric_columns].replace({',': ''}, regex=True)

    df['priceDiff'] = df['ceilingPrice'] - df['floorPrice']
    print(df.dtypes)
    print(df.head(50))
    df.to_csv(out_csv_file_path, index=False)
    return True

def load():
    table_name = 'StockSessionInfo' 
    conn = connect(
        host="172.19.0.2",
        database="airflow-db",
        user="airflow",
        password="airflow",
        port='5432'
    )
    cur = conn.cursor()

    # Create a table in PostgreSQL
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS public.{table_name} (
            code varchar(128),
            date DATE,
            time TIME,
            floor varchar(512),
            type varchar(512),
            basicPrice FLOAT,
            ceilingPrice FLOAT,
            floorPrice FLOAT,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            average FLOAT,
            adOpen FLOAT,
            adHigh FLOAT,
            adLow FLOAT,
            adClose FLOAT,
            adAverage FLOAT,
            nmVolume FLOAT,
            nmValue FLOAT,
            ptVolume FLOAT,
            ptValue FLOAT,
            change FLOAT,
            adChange FLOAT,
            pctChange FLOAT,
            priceDiff FLOAT
        );"""
    
    cur.execute(create_table_query)
    conn.commit()

     # Get the latest date in the database
    cur.execute(f"SELECT MAX(date) FROM public.{table_name}")
    latest_date = cur.fetchone()[0]
    if latest_date is None:
        latest_date = datetime.strptime('1999-01-01', '%Y-%m-%d').date()
    print(latest_date)

    csv_file_path = 'data/stock_price.csv'
    new_transactions = []

    # Read data from the CSV file and filter out transactions newer than the latest date in the database
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            csv_date = datetime.strptime(row[1], '%Y-%m-%d').date()  # Assuming 'date' column is the second one
            if csv_date < latest_date:
                new_transactions.append(row)

    # Prepare the insert query with placeholders
    insert_query = f"INSERT INTO public.{table_name} VALUES %s"
    if new_transactions:
        extras.execute_values(cur, insert_query, new_transactions)  # Bulk insertion of new rows
        
    conn.commit()
    cur.close()
    conn.close()
    return True


def train_model():
    from sklearn.preprocessing import MinMaxScaler
    dataset_train = pd.read_csv('data/stock_price.csv')
    dataset_train['date'] = pd.to_datetime(dataset_train['date'])
    # Filter data for the years 2018 and 2019
    dataset_test = dataset_train[(dataset_train['date'].dt.year == 2018) | (dataset_train['date'].dt.year == 2019)]
    training_set = dataset_train.iloc[:, 5:6].values

    # Thuc hien scale du lieu gia ve khoang 0,1
    sc = MinMaxScaler(feature_range=(0, 1))
    training_set_scaled = sc.fit_transform(training_set)

    # Tao du lieu train, X = 60 time steps, Y =  1 time step
    X_train = []
    y_train = []
    no_of_sample = len(training_set)

    for i in range(60, no_of_sample):
        X_train.append(training_set_scaled[i - 60:i, 0])
        y_train.append(training_set_scaled[i, 0])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Xay dung model LSTM
    regressor = Sequential()
    regressor.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=50))
    regressor.add(Dropout(0.2))
    regressor.add(Dense(units=1))
    regressor.compile(optimizer='adam', loss='mean_squared_error')

    regressor.fit(X_train, y_train, epochs=1, batch_size=32)
    regressor.save("resource/stockmodel.h5")
        # Load du lieu tu 1/1/2019 - 2/10/2019
    # dataset_test = pd.read_csv('data/vcb_2019.csv')
    real_stock_price = dataset_test.iloc[:, 1:2].values

    # Tien hanh du doan
    dataset_total = pd.concat((dataset_train['close'], dataset_test['close']), axis = 0)
    inputs = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
    inputs = inputs.reshape(-1,1)
    inputs = sc.transform(inputs)

    X_test = []
    no_of_sample = len(inputs)

    for i in range(60, no_of_sample):
        X_test.append(inputs[i-60:i, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)

    # Ve bieu do gia that va gia du doan
    plt.plot(real_stock_price, color = 'red', label = 'Real VCB Stock Price')
    plt.plot(predicted_stock_price, color = 'blue', label = 'Predicted VCB Stock Price')
    plt.title('VCB Stock Price Prediction')
    plt.xlabel('Time')
    plt.ylabel('VCB Stock Price')
    plt.legend()
    plt.show()

    # Du doan tiep gia cac ngay tiep theo den 30/10

    dataset_test = dataset_test['close'][len(dataset_test)-60:len(dataset_test)].to_numpy()
    dataset_test = np.array(dataset_test)

    inputs = dataset_test
    inputs = inputs.reshape(-1,1)
    inputs = sc.transform(inputs)


    i = 0
    while i<28:
        X_test = []
        no_of_sample = len(dataset_test)

        # Lay du lieu cuoi cung
        X_test.append(inputs[no_of_sample - 60:no_of_sample, 0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        # Du doan gia
        predicted_stock_price = regressor.predict(X_test)

        # chuyen gia tu khoang (0,1) thanh gia that
        predicted_stock_price = sc.inverse_transform(predicted_stock_price)

        # Them ngay hien tai vao
        dataset_test = np.append(dataset_test, predicted_stock_price[0], axis=0)
        inputs = dataset_test
        inputs = inputs.reshape(-1, 1)
        inputs = sc.transform(inputs)

        print('Stock price ' + str(i+3) + '/10/2019 of VCB : ', predicted_stock_price[0][0])
        i = i +1
    return True


def email():
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    import base64
    from datetime import datetime

    out_csv_file_path = 'data/stock_price.csv'

    # Set up the email components
    msg = MIMEMultipart()
    msg['From'] = 'nguyent.hung.pntv9@gmail.com'
    msg['To'] = 'nguyent.hung.f17@gmail.com'
    msg['Subject'] = 'Notification for someone'
    msg.attach(MIMEText('<img src="https://miai.vn/wp-content/uploads/2022/01/Logo_web.png"> Hello,<br>Welcome. Your file is in attachment<br>Thank you!'))

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
    'etl_procesing',
    default_args={
        'owner': 'nguyenthung',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A ML training pipline DAG',
    schedule_interval=timedelta(days=1),
    start_date= datetime.today() - timedelta(days=1),
    tags=['nguyenthung'])


crawl_data = PythonOperator(
    task_id='crawl_data',
    python_callable=craw_stock_price,
    op_kwargs={"to_date": "{{ ds }}"},
    dag=dag
)
transform_operator = PythonOperator(
    task_id='transform_phase',
    python_callable=transform,
    dag=dag
)
load_operator = PythonOperator(
    task_id='load_phase',
    python_callable=load,
    dag=dag
)
train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

send_email = PythonOperator(
    task_id='email_operator',
    python_callable=email,
    dag=dag
)

crawl_data>>transform_operator>>load_operator >>train_model >> send_email