#Khai báo thư viện và các biến liên quan
import time
import paho.mqtt.client as mqtt
from ftplib import FTP
import sqlite3
import threading
import csv
import json
import os
import serial
import winreg
from filterpy.kalman import KalmanFilter
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# Khởi tạo Kalman Filter
kalman_filter = KalmanFilter(dim_x=1, dim_z=1)
kalman_filter.x = np.array([[0.]])  # Giá trị ban đầu ước lượng

# Thiết lập các ma trận cho Kalman Filter
kalman_filter.F = np.array([[1.]])  # Ma trận trạng thái
kalman_filter.H = np.array([[1.]])  # Ma trận quan sát
kalman_filter.P = np.array([[1.]])  # Ma trận hiệp phương sai lỗi
kalman_filter.R = np.array([[1.]])  # Ma trận nhiễu đo lường
kalman_filter.Q = np.array([[0.1]])  # Ma trận nhiễu hệ thống

# Thiết lập thông tin kết nối MQTT
broker = "broker.emqx.io"
port = 1883

# Khởi tạo bộ lọc Kalman



# Đọc giá trị analog từ MCP3208
import time
import random
# Khởi tạo SPI

# Hàm đọc kênh ADC
def read_adc(channel):
    while True:
        data = random.randint(1020, 1023)
        logging.debug(f"ADC Read (Channel {channel}): {data}")
        time.sleep(1) 
        return data

#khai báo global cho các biến cài đặt từ MQTT
#Thiết bị
nameequip1= typeequip1= descritp1= method1 = 0
nameequip2= typeequip2= descritp2= method2 = 0
nameequip3= typeequip3= descritp3= method3 = 0
nameequip4= typeequip4= descritp4= method4 = 0
#sensor1
name1= unit1= min_value1=0
min_alarm1=1
max_value1=2
max_alarm1=status1=0
#sensor2
name2= unit2= 0
min_value2=1
min_alarm2=0
max_value2=2
max_alarm2=status2=0
#sensor3
name3=unit3=min_alarm3=0
max_value3=2
min_value3=1
max_alarm3=status3=0
#sensor4
name4=unit4= 0
min_value4=5
min_alarm4=max_alarm4=status4=0
max_value4=100
data_received_flag = False
# Hàm xử lý khi nhận tin nhắn từ cảm biến 1
def on_message_sensor1(client, userdata, msg):
    
    global name1, unit1, min_alarm1, max_value1,min_value1,max_alarm1,status1,data_received_flag

    message = str(msg.payload.decode("utf-8"))
    data = json.loads(message)

    # Trích xuất các trường từ dữ liệu JSON
    name1 = data["Name"]
    unit1 = data["Unit"]
    min_value1 = data["Min_Value"]
    max_value1 = data["Max_Value"]
    min_alarm1 = data["Min_Alarm"]
    max_alarm1 = data["Max_Alarm"]
    status1 = data["Status"]
    data_received_flag = True
    print(data_received_flag)


def mqtt_listener1():
    client = mqtt.Client()
    client.connect(broker, port)
    
    client.message_callback_add("sensor/1", on_message_sensor1)
    client.on_message = on_message_sensor1
    client.subscribe('sensor/1')

    client.loop_forever()
mqtt_thread = threading.Thread(target=mqtt_listener1)
mqtt_thread.start()

    # Xử lý dữ liệu nhận được từ cảm biến 1
def kalmanfilter1():
    rawvalue = read_adc(0)
    logging.debug(f"Raw Value: {rawvalue}")

    kalman_filter.predict()
    kalman_filter.update(np.array([[rawvalue]]))
    
    rawvalue = rawvalue * (float(max_value1) - float(min_value1))/4096 + float(min_value1)
    filtered_value = kalman_filter.x[0][0]  # Lấy giá trị từ mảng
    logging.debug(f"Filtered Value: {filtered_value}")
    return filtered_value
def data_filter1(output_dir):
    def save_to_sqlite(table_name, timestamp, value):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (timestamp REAL, value REAL)")
        cursor.execute(f"INSERT INTO {table_name} (timestamp, value) VALUES (?, ?)", (timestamp, value))
        conn.commit()
        conn.close()

    def save_to_csv(file_name, name, timestamp, value, unit):
        current_date = time.strftime("%Y-%m-%d")
        file_path = os.path.join(output_dir, f"{file_name}_{current_date}.csv")
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name,timestamp, value , unit])

    first_last_values = []
    start_time = time.time()
    global data_received_flag
    print(data_received_flag)

    while True:
        if data_received_flag:  # Chỉ đọc và ghi dữ liệu khi nhận được tin nhắn
            raw_value = kalmanfilter1()
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time >= 10:
                if len(first_last_values) == 2:
                    k = (first_last_values[0] + first_last_values[1]) / 2
                    min_value = 0.98 * k
                    max_value = 1.02 * k
                    within_range = all(min_value <= value <= max_value for value in first_last_values)

                    if within_range:
                        save_to_sqlite("Data", current_time, k)
                        save_to_csv("Sensor1_Data", name1, current_time, k, unit1)
                    else:
                        if any(value < min_value or value > max_value for value in first_last_values):
                            save_to_sqlite("Alarm", current_time, k)
                            save_to_csv("Sensor1_Alarm", name1, current_time, k, unit1)
                        else:
                            save_to_sqlite("Data", current_time, k)
                            save_to_csv("Sensor1_Data", name1, current_time, k, unit1)

                    first_last_values = [raw_value]
                    start_time = current_time
                else:
                    first_last_values.append(raw_value)
            else:
                if len(first_last_values) < 2:
                    first_last_values.append(raw_value)

              # Reset cờ sau khi xử lý xong
        time.sleep(0.5)
# Hàm xử lý khi nhận tin nhắn từ cảm biến 2
def on_message_sensor2(client, userdata, msg):
    global name2, unit2, min_alarm2, max_alarm2, min_value2, max_value2, status2
    message = str(msg.payload.decode("utf-8"))
    data = json.loads(message)

    # Trích xuất các trường từ dữ liệu JSON
    name2 = data["Name"]
    unit2 = data["Unit"]
    min_value2 = data["Min_Value"]
    max_value2 = data["Max_Value"]
    min_alarm2 = data["Min_Alarm"]
    max_alarm2 = data["Max_Alarm"]
    status2 = data["Status"]

    # Xử lý dữ liệu nhận được từ cảm biến 2


def mqtt_listener2():
    client = mqtt.Client()
    client.connect(broker, port)
    
    client.message_callback_add("sensor/2", on_message_sensor1)
    client.on_message = on_message_sensor1
    client.subscribe('sensor/2')

    client.loop_forever()
mqtt_thread = threading.Thread(target=mqtt_listener2)
mqtt_thread.start()


def kalmanfilter2():
    rawvalue = read_adc(1)

    # Áp dụng bộ lọc Kalman
    kalman_filter.predict()
    kalman_filter.update(rawvalue)
    rawvalue = rawvalue*( float(max_value2) - float(min_value2))/4096 + float(min_value2)
    filtered_value = kalman_filter.x[0]
    
    return filtered_value
def data_filter2(output_dir):

    def save_to_sqlite(table_name, timestamp, value):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (timestamp REAL, value REAL)")
        cursor.execute(f"INSERT INTO {table_name} (timestamp, value) VALUES (?, ?)", (timestamp, value))
        conn.commit()
        conn.close()

    def save_to_csv(file_name,name, timestamp, value, unit):
        current_date = time.strftime("%Y-%m-%d")
        file_path = os.path.join(output_dir, f"{file_name}_{current_date}.csv")
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, timestamp, value, unit])

    first_last_values = []
    start_time = time.time()

    while True:
     raw_value = kalmanfilter2()
     current_time = time.time()
     elapsed_time = current_time - start_time

     if elapsed_time >= 10:
        if len(first_last_values) == 2:
            k = (first_last_values[0] + first_last_values[1]) / 2
            min_value = 0.98 * k
            max_value = 1.02 * k
            within_range = all(min_value <= value <= max_value for value in first_last_values)

            if within_range:
                k=10
                save_to_sqlite("Data", current_time, k)
                save_to_csv("Sensor2_Data", name2, current_time, k, unit2)
            else:
                if any(value < min_value or value > max_value for value in first_last_values):
                    k=10
                    save_to_sqlite("Alarm", current_time, k)
                    save_to_csv("Sensor2_Alarm", name2, current_time, k, unit2)
                else:
                    k = 10
                    save_to_sqlite("Data", current_time, k)
                    save_to_csv( "Sensor2_Data",name2,current_time,  k, unit2)

            first_last_values = [raw_value]
            start_time = current_time
        else:
            first_last_values.append(raw_value)
     else:
        if len(first_last_values) < 2:
            first_last_values.append(raw_value)

     time.sleep(0.1)


# Hàm xử lý khi nhận tin nhắn từ cảm biến 3
def on_message_sensor3(client, userdata, msg):
    global name3, unit3, min_alarm3, max_alarm3, min_value3, max_value3, status3
    message = str(msg.payload.decode("utf-8"))
    data = json.loads(message)

    # Trích xuất các trường từ dữ liệu JSON
    name3 = data["Name"]
    unit3 = data["Unit"]
    min_value3 = data["Min_Value"]
    max_value3 = data["Max_Value"]
    min_alarm3 = data["Min_Alarm"]
    max_alarm3 = data["Max_Alarm"]
    status3 = data["Status"]

    # Xử lý dữ liệu nhận được từ cảm biến 2


def mqtt_listener3():
    client = mqtt.Client()
    client.connect(broker, port)
    
    client.message_callback_add("sensor/3", on_message_sensor1)
    client.on_message = on_message_sensor3
    client.subscribe('sensor/3')

    client.loop_forever()
mqtt_thread = threading.Thread(target=mqtt_listener3)
mqtt_thread.start()


def kalmanfilter3():
    rawvalue = read_adc(2)

    # Áp dụng bộ lọc Kalman
    kalman_filter.predict()
    kalman_filter.update(rawvalue)
    rawvalue = rawvalue*4096/( float(max_value3) - float(min_value3)) + float(min_value3)
    filtered_value = kalman_filter.x[0]
    
    return filtered_value
def data_filter3(output_dir):

    def save_to_sqlite(table_name, timestamp, value):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (timestamp REAL, value REAL)")
        cursor.execute(f"INSERT INTO {table_name} (timestamp, value) VALUES (?, ?)", (timestamp, value))
        conn.commit()
        conn.close()

    def save_to_csv(file_name,name, timestamp, value,unit):
        current_date = time.strftime("%Y-%m-%d")
        file_path = os.path.join(output_dir, f"{file_name}_{current_date}.csv")
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, timestamp, value, unit])

    first_last_values = []
    start_time = time.time()

    while True:
     raw_value = kalmanfilter3()
     current_time = time.time()
     elapsed_time = current_time - start_time

     if elapsed_time >= 10:
        if len(first_last_values) == 2:
            k = (first_last_values[0] + first_last_values[1]) / 2
            min_value = 0.98 * k
            max_value = 1.02 * k
            within_range = all(min_value <= value <= max_value for value in first_last_values)

            if within_range:
                save_to_sqlite("Data", current_time, k)
                save_to_csv("Sensor3_Data", name3, current_time, k, unit3)
            else:
                if any(value < min_value or value > max_value for value in first_last_values):
                    save_to_sqlite("Alarm", current_time, k)
                    save_to_csv("Sensor3_Alarm", name3, current_time, k, unit3)
                else:
                    save_to_sqlite("Data", current_time, k)
                    save_to_csv("Sensor3_Data", name3, current_time, k, unit3)

            first_last_values = [raw_value]
            start_time = current_time
        else:
            first_last_values.append(raw_value)
     else:
        if len(first_last_values) < 2:
            first_last_values.append(raw_value)

     time.sleep(0.1)
 
# Hàm xử lý khi nhận tin nhắn từ cảm biến 4
def on_message_sensor4(client, userdata, msg):
    global name4, unit4, min_alarm4, max_alarm4, min_value4, max_value4, status4
    message = str(msg.payload.decode("utf-8"))
    data = json.loads(message)

    # Trích xuất các trường từ dữ liệu JSON
    name4 = data["Name"]
    unit4 = data["Unit"]
    min_value4 = data["Min_Value"]
    max_value4 = data["Max_Value"]
    min_alarm4 = data["Min_Alarm"]
    max_alarm4 = data["Max_Alarm"]
    status4 = data["Status"]

    # Xử lý dữ liệu nhận được từ cảm biến 2


def mqtt_listener4():
    client = mqtt.Client()
    client.connect(broker, port)
    
    client.message_callback_add("sensor/4", on_message_sensor1)
    client.on_message = on_message_sensor4
    client.subscribe('sensor/4')

    client.loop_forever()
mqtt_thread = threading.Thread(target=mqtt_listener4)
mqtt_thread.start()


def kalmanfilter4():
    rawvalue4 = read_adc(3)
    
    # Chuyển đổi giá trị về thang đo 5-100
    rawvalue3_converted = rawvalue4 / 4096 * 95 + 5
    print(f"Giá trị ADC chuyển đổi: {rawvalue3_converted}")

    # Áp dụng bộ lọc Kalman
    kalman_filter.predict()
    kalman_filter.update(rawvalue3_converted)

    # Giá trị sau khi lọc
    filtered_value = kalman_filter.x[0]
    print(f"Giá trị sau khi lọc: {filtered_value}")

    return filtered_value
def data_filter4(output_dir):

    def save_to_sqlite(table_name, timestamp, value):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (timestamp REAL, value REAL)")
        cursor.execute(f"INSERT INTO {table_name} (timestamp, value) VALUES (?, ?)", (timestamp, value))
        conn.commit()
        conn.close()
    def save_to_csv(file_name,name, timestamp, value, unit):
        current_date = time.strftime("%Y-%m-%d")
        file_path = os.path.join(output_dir, f"{file_name}_{current_date}.csv")
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, timestamp, value, unit])

    first_last_values = []
    start_time = time.time()

    while True:
     raw_value4 = kalmanfilter4()
     print(raw_value4)
     current_time = time.time()
     elapsed_time = current_time - start_time

     if elapsed_time >= 10:
        if len(first_last_values) == 2:
            k = (first_last_values[0] + first_last_values[1]) / 2
            min_value = 0.98 * k
            max_value = 1.02 * k
            within_range = all(min_value <= value <= max_value for value in first_last_values)

            if within_range:
                save_to_sqlite("Data", current_time, k)
                save_to_csv("Sensor4_Data", name4, current_time, k, unit4)
            else:
                if any(value < min_value or value > max_value for value in first_last_values):
                    save_to_sqlite("Alarm", current_time, k)
                    save_to_csv("Sensor4_Alarm", name4, current_time, k, unit4)
                else:
                    save_to_sqlite("Data", current_time, k)
                    save_to_csv("Sensor4_Data", name4, current_time, k, unit4)

            first_last_values = [raw_value4]
            start_time = current_time
        else:
            first_last_values.append(raw_value4)
     else:
        if len(first_last_values) < 2:
            first_last_values.append(raw_value4)

     time.sleep(0.1)


if __name__ == "__main__":
    # Tạo một luồng riêng để thực hiện hàm data_filter
    output_dir = "./data"
    data_filter_thread_1 = threading.Thread(target=data_filter1,args=(output_dir,))
    data_filter_thread_1.start()
    data_filter_thread_2 = threading.Thread(target=data_filter2,args=(output_dir,))
    data_filter_thread_2.start()
    data_filter_thread_3 = threading.Thread(target=data_filter3,args=(output_dir,))
    data_filter_thread_3.start()
    data_filter_thread_4 = threading.Thread(target=data_filter4,args=(output_dir,))
    data_filter_thread_4.start()
   
# Khởi tạo kết nối serial với module RS485 to USB




# Kết nối và đăng ký nhận tin nhắn MQTT
client = mqtt.Client()
client.connect(broker, port)

# Đăng ký các hàm xử lý tin nhắn cho từng cảm biến
client.message_callback_add("sensor/1", on_message_sensor1)
client.message_callback_add("sensor/2", on_message_sensor2)
client.message_callback_add("sensor/3", on_message_sensor3)
client.message_callback_add("sensor/4", on_message_sensor4)

# Subscribe vào các topic để nhận gói tin từ mỗi cảm biến
topics = ["sensor/1", "sensor/2", "sensor/3", "sensor/4"]
for topic in topics:
    client.subscribe(topic)

# Vòng lặp chính để duy trì kết nối MQTT
client.loop_forever()

