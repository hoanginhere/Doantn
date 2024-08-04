# Khai báo thư viện và các biến liên quan
import time
import paho.mqtt.client as mqtt
from ftplib import FTP
import sqlite3
import threading
import csv
import json
import os
import random
import logging
import serial
import RPi.GPIO as GPIO
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#rs485
#rs485 = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
# Thiết lập thông tin kết nối MQTT
broker = "broker.emqx.io"
port = 1883
# Hàm đọc kênh ADC
def read_adc(channel):
    while True:
        data = random.randint(1020, 1023)
        logging.debug(f"ADC Read (Channel {channel}): {data}")
        time.sleep(1)
        return data
# Đọc giá trị digital 
GPIO.setmode(GPIO.BCM)
SPI setup
def read_sensor_digital(Enable, M, m, DIGITAL_PIN):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DIGITAL_PIN, GPIO.IN)
        sensor_value = GPIO.input(DIGITAL_PIN)
        time.sleep(1)
        if Enable == False or Enable == None:
            return sensor_value
        else:
            real_data = ((M-m)/4095)*sensor_value + m
            return real_data
    except KeyboardInterrupt:
        GPIO.cleanup()
# Khai báo global cho các biến cài đặt từ MQTT
# Thiết bị
nameequip1 = typeequip1 = descritp1 = method1 = 0
nameequip2 = typeequip2 = descritp2 = method2 = 0
nameequip3 = typeequip3 = descritp3 = method3 = 0
nameequip4 = typeequip4 = descritp4 = method4 = 0
# sensor1
name1 = unit1 =  0
min_value1 = 5
min_alarm1 = 1
max_value1 = 100
max_alarm1 = status1 = 0
# sensor2
name2 = unit2 = 0
min_value2 = 5
min_alarm2 = 0
max_value2 = 100
max_alarm2 = status2 = 0
# sensor3
name3 = unit3 = min_alarm3 = 0
max_value3 = 2
min_value3 = 1
max_alarm3 = status3 = 0
# sensor4
name4 = unit4 = 0
min_value4 = 5
min_alarm4 = max_alarm4 = status4 = 0
max_value4 = 100
data_received_flag1 = False
data_received_flag2 = False

# Hàm xử lý khi nhận tin nhắn từ cảm biến 1
def on_message_sensor1(client, userdata, msg):
    global name1, unit1, min_alarm1, max_value1, min_value1, max_alarm1, status1, data_received_flag1

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
    print(max_value1)

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
def process_sensor1():
    rawvalue = read_adc(0)
    logging.debug(f"Raw Value: {rawvalue}")
    print(rawvalue)

    rawvalue = rawvalue * (float(max_value1) - float(min_value1)) / 4096 + float(min_value1)
    logging.debug(f"Processed Value: {rawvalue}")
    print(rawvalue)
    return rawvalue

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
            writer.writerow([name, timestamp, value, unit])

    first_last_values = []
    start_time = time.time()
    global data_received_flag1
    print(data_received_flag1)

    while True:
        if data_received_flag1:  # Chỉ đọc và ghi dữ liệu khi nhận được tin nhắn
            raw_value = process_sensor1()
            print(raw_value)
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time >= 10:
                if len(first_last_values) == 2:
                    k = (first_last_values[0] + first_last_values[1]) / 2
                    min_value = 0.98 * k
                    max_value = 1.02 * k
                    within_range = all(min_value <= value <= max_value for value in first_last_values)

                    if within_range:
                        save_to_sqlite("Input1", current_time, k)
                        save_to_csv("Input1_Data", name1, current_time, k, unit1)
                    else:
                        if any(value < min_alarm1 or value > max_alarm1 for value in first_last_values):
                            save_to_sqlite("Alarm", current_time, k)
                            save_to_csv("Input1_Alarm", name1, current_time, k, unit1)
                        else:
                            save_to_sqlite("Input1", current_time, k)
                            save_to_csv("Input1_Data", name1, current_time, k, unit1)

                    first_last_values = [raw_value]
                    start_time = current_time
                else:
                    first_last_values.append(raw_value)
            else:
                if len(first_last_values) < 2:
                    first_last_values.append(raw_value)

        time.sleep(5)

# Hàm xử lý khi nhận tin nhắn từ cảm biến 2
def on_message_sensor2(client, userdata, msg):
    global name2, unit2, min_alarm2, max_alarm2, min_value2, max_value2, status2,data_received_flag2
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
    data_received_flag2 = True
    print(data_received_flag1)

def mqtt_listener2():
    client = mqtt.Client()
    client.connect(broker, port)

    client.message_callback_add("sensor/2", on_message_sensor2)
    client.on_message = on_message_sensor2
    client.subscribe('sensor/2')

    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_listener2)
mqtt_thread.start()

def process_sensor2():
    rawvalue = read_adc(1)
    rawvalue = rawvalue * (float(max_value2) - float(min_value2)) / 4096 + float(min_value2)
    logging.debug(f"Processed Value: {rawvalue}")
    return rawvalue

def data_filter2(output_dir):
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
            writer.writerow([name, timestamp, value, unit])

    first_last_values = []
    start_time = time.time()
    global data_received_flag2
    print(data_received_flag2)

    while True:
        if data_received_flag1:  # Chỉ đọc và ghi dữ liệu khi nhận được tin nhắn
            raw_value = process_sensor1()
            print(raw_value)
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time >= 10:
                if len(first_last_values) == 2:
                    k = (first_last_values[0] + first_last_values[1]) / 2
                    min_value = 0.98 * k
                    max_value = 1.02 * k
                    within_range = all(min_value <= value <= max_value for value in first_last_values)

                    if within_range:
                        save_to_sqlite("Input2", current_time, k)
                        save_to_csv("Input2_Data", name2, current_time, k, unit2)
                    else:
                        if any(value < min_alarm2 or value > max_alarm2 for value in first_last_values):
                            save_to_sqlite("Alarm", current_time, k)
                            save_to_csv("Input2_Alarm", name2, current_time, k, unit2)
                        else:
                            save_to_sqlite("Input1", current_time, k)
                            save_to_csv("Input2_Data", name2, current_time, k, unit2)

                    first_last_values = [raw_value]
                    start_time = current_time
                else:
                    first_last_values.append(raw_value)
            else:
                if len(first_last_values) < 2:
                    first_last_values.append(raw_value)

        time.sleep(5)


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
    data_received_flag3 = True
    print(data_received_flag3)


def mqtt_listener3():
    client = mqtt.Client()
    client.connect(broker, port)

    client.message_callback_add("sensor/3", on_message_sensor3)
    client.on_message = on_message_sensor3
    client.subscribe('sensor/3')

    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_listener2)
mqtt_thread.start()

def process_sensor3():
    rawvalue = read_adc(1)
    rawvalue = rawvalue * (float(max_value3) - float(min_value3)) / 4096 + float(min_value3)
    logging.debug(f"Processed Value: {rawvalue}")
    return rawvalue

def data_filter3(output_dir):
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
            writer.writerow([name, timestamp, value, unit])

    first_last_values = []
    start_time = time.time()

    while True:
        raw_value = process_sensor3()
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
                    save_to_csv("Input3_Data", name3, current_time, k, unit3)
                else:
                    if any(value < min_value or value > max_value for value in first_last_values):
                        save_to_sqlite("Alarm", current_time, k)
                        save_to_csv("Input3_Alarm", name3, current_time, k, unit3)
                    else:
                       
                        save_to_sqlite("Data", current_time, k)
                        save_to_csv("Input3_Data", name3, current_time, k, unit3)

                first_last_values = [raw_value]
                start_time = current_time
            else:
                first_last_values.append(raw_value)
        else:
            if len(first_last_values) < 2:
                first_last_values.append(raw_value)

        time.sleep(0.5)
'''def read_temperature_humidity(output_dir):
        # Đọc dữ liệu qua RS485
    rs485.write(b'\x03\x04\x00\x00\x00\x02\xC4\x0B')
    response = rs485.read(7)
    if len(response) == 7 and response[0] == 3 and response[1] == 4:
        temperature_rs485 = (response[3] * 256 + response[4]) / 100.0
        humidity_rs485 = (response[5] * 256 + response[6]) / 100.0

    return temperature_rs485'''

if __name__ == "__main__":
    output_dir = "./data_output"
    os.makedirs(output_dir, exist_ok=True)

    data_thread1 = threading.Thread(target=data_filter1, args=(output_dir,))
    data_thread2 = threading.Thread(target=data_filter2, args=(output_dir,))
    data_thread3 = threading.Thread(target=data_filter3, args=(output_dir,))
    #data_thread485 = threading.Thread(target=read_temperature_humidity, args=(output_dir,))

    data_thread1.start()
    data_thread2.start()
    data_thread3.start()

    data_thread1.join()
    data_thread2.join()
    data_thread3.join()


client = mqtt.Client()
client.connect(broker, port)

# Đăng ký các hàm xử lý tin nhắn cho từng cảm biến
client.message_callback_add("sensor/1", on_message_sensor1)
client.message_callback_add("sensor/2", on_message_sensor2)
client.message_callback_add("sensor/3", on_message_sensor3)
#client.message_callback_add("sensor/4", on_message_sensor4)

# Subscribe vào các topic để nhận gói tin từ mỗi cảm biến
topics = ["sensor/1", "sensor/2", "sensor/3", "sensor/4"]
for topic in topics:
    client.subscribe(topic)

# Vòng lặp chính để duy trì kết nối MQTT
client.loop_forever()
