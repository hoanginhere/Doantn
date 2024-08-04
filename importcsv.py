import os
import csv
import random
from datetime import datetime
import time

def generate_random_data():
    temperature = round(random.uniform(20, 30), 2)  # Nhiệt độ trong khoảng 20-30 độ Celsius
    humidity = round(random.uniform(40, 60), 2)  # Độ ẩm trong khoảng 40-60%

    return temperature, humidity
Unit= "temperature"
def save_to_csv(data, filename):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Timestamp', Unit, 'Humidity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            # Chỉ viết header nếu file trống
            writer.writeheader()

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        writer.writerow({'Timestamp': timestamp, 'Temperature': data[0], 'Humidity': data[1]})

if __name__ == "__main__":
    csv_filenames = [
        'D:/sensor_data.csv',
        'D:/sensor_data2.csv',
        'D:/sensor_data3.csv'
    ]

    try:
        while True:
            for i, filename in enumerate(csv_filenames):
                data = generate_random_data()
                save_to_csv(data, filename)
                print(f"Data saved to {filename}: {data}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Measurement stopped by user.")







def data_filtering():
    data = []  # Danh sách lưu trữ dữ liệu lọc
    
    while True:
        start_time = time.time()  # Thời điểm bắt đầu lọc
        
        # Kiểm tra trong khoảng thời gian t=10 giây
        while time.time() - start_time < 10:
            value = data  # Đọc giá trị từ Rasberry Pi
            
            # Kiểm tra giá trị bất thường
            if is_outlier(value):
                store_outlier(value)  # Lưu giá trị bất thường vào bảng riêng
                start_time = time.time()  # Reset thời điểm bắt đầu lọc
            else:
                data.append(value)  # Lưu giá trị vào danh sách dữ liệu lọc
        
        if len(data) >= 2:
            store_data(data[0], data[-1])  # Lưu 2 giá trị đầu và cuối vào bảng
        data = []  # Reset danh sách dữ liệu lọc

# Hàm đọc giá trị từ Rasberry Pi (giả định)
def read_data():
    # Đọc giá trị từ Rasberry Pi và trả về
    value = 0.5  # Giá trị giả định
    return value

# Hàm kiểm tra giá trị bất thường (giả định)
def is_outlier(value):
    # Kiểm tra giá trị và trả về True nếu là giá trị bất thường, False nếu không
    if value > 0.8:
        return True
    return False

# Hàm lưu giá trị bất thường vào bảng riêng (giả định)
def store_outlier(value):
    # Lưu giá trị bất thường vào bảng riêng
    print("Detected outlier:", value)

# Hàm lưu 2 giá trị đầu và cuối vào bảng (giả định)
def store_data(first_value, last_value):
    # Lưu 2 giá trị đầu và cuối vào bảng
    print("Stored data:", first_value, last_value)

# Gọi hàm lọc dữ liệu
data_filtering()







