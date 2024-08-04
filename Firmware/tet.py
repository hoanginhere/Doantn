import serial
import time
import csv

# Cấu hình cổng serial
ser = serial.Serial('COM5', 9600, timeout=1)  # Thay 'COM3' bằng cổng của bạn
time.sleep(2)  # Chờ cổng serial ổn định

# Mở file CSV để ghi
csv_filename = 'sht20_data.csv'

def read_data():
    ser.write(b'READ')  # Gửi lệnh READ
    time.sleep(1)
    data = ser.read(14)  # Đọc đúng 14 byte dữ liệu
    print(data)
    return data.decode(errors='ignore')  # Bỏ qua lỗi giải mã

def extract_data(raw_data):
    # Xóa bỏ ký tự không mong muốn và tách dữ liệu nhiệt độ và độ ẩm
    try:
        data = raw_data.replace('\xa1', '').replace('\xe6', '')
        parts = data.split(',')
        if len(parts) == 2:
            temperature = parts[0].strip()
            humidity = parts[1].strip()
            return temperature, humidity
        else:
            return None, None
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None, None

def write_to_csv(filename, data):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Time', 'Temperature', 'Humidity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if csvfile.tell() == 0:
            writer.writeheader()
        
        writer.writerow(data)

if __name__ == "__main__":
    try:
        while True:
            response = read_data()
            temperature, humidity = extract_data(response)
            if temperature and humidity:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                data_to_write = {'Time': current_time, 'Temperature': temperature, 'Humidity': humidity}
                write_to_csv(csv_filename, data_to_write)
                print(f"Time: {current_time}, Temperature: {temperature}, Humidity: {humidity}")
            else:
                print("Invalid data received.")
            
            time.sleep(5)  # Đọc dữ liệu mỗi 5 giây
    except KeyboardInterrupt:
        print("Quitting program...")
    finally:
        ser.close()
