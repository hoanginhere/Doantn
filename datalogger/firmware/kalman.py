from filterpy.kalman import KalmanFilter
import time
import random
import sqlite3
import csv
import json
import os
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# Khởi tạo SPI
kalman_filter = KalmanFilter(dim_x=1, dim_z=1)
kalman_filter.x = np.array([[0.]])  # Giá trị ban đầu ước lượng

# Thiết lập các ma trận cho Kalman Filter
kalman_filter.F = np.array([[1.]])  # Ma trận trạng thái
kalman_filter.H = np.array([[1.]])  # Ma trận quan sát
kalman_filter.P = np.array([[1.]])  # Ma trận hiệp phương sai lỗi
kalman_filter.R = np.array([[1.]])  # Ma trận nhiễu đo lường
kalman_filter.Q = np.array([[0.1]])  # Ma trận nhiễu hệ thống
# Hàm đọc kênh ADC
name4=unit4= 0
min_value4=5
min_alarm4=max_alarm4=status4=0
max_value4=100
def read_adc(channel):
    while True:
        data = random.randint(1020, 1023)
        logging.debug(f"ADC Read (Channel {channel}): {data}")
        time.sleep(1) 
        return data
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

     time.sleep(1)
output_dir = "./data"
data_filter4(output_dir)