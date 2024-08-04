import tkinter as tk
from tkinter import ttk
import random
import struct

# Mô phỏng đọc dữ liệu từ cảm biến SHT20 qua RS485
def read_sensor_data():
    # Mô phỏng nhiệt độ và độ ẩm
    temperature = round(random.uniform(26.5, 27.5), 2)
    humidity = round(random.uniform(50.0, 60.0), 2)
    
    # Chuyển đổi nhiệt độ và độ ẩm thành dạng hexa (giả sử dữ liệu có dạng 2 byte mỗi giá trị)
    temperature_int = int(temperature * 10)
    humidity_int = int(humidity * 10)
    
    # Mô phỏng khung dữ liệu nhận được
    # Địa chỉ Slave, Mã hàm, Số byte, Nhiệt độ (2 byte), Độ ẩm (2 byte), CRC (2 byte)
    data_frame = struct.pack('>BBBHHH', 0x01, 0x04, 0x04, temperature_int, humidity_int, 0x1234)
    
    # Chuyển đổi khung dữ liệu thành dạng chuỗi byte
    data_str = ' '.join(f'{byte:02x}' for byte in data_frame)
    
    return temperature, humidity, data_str

# Hàm cập nhật dữ liệu trên GUI
def update_data():
    temperature, humidity, data_str = read_sensor_data()
    
    # Cập nhật nhãn hiển thị nhiệt độ
    temperature_label.config(text=f"Nhiệt độ: {temperature} °C")
    
    # Cập nhật nhãn hiển thị độ ẩm
    humidity_label.config(text=f"Độ ẩm: {humidity} %")
    
    # Cập nhật nhãn hiển thị dữ liệu nhận được
    data_label.config(text=f"Dữ liệu nhận được: b'{data_str}'")
    
    # Gọi lại hàm này sau 1 giây
    root.after(1000, update_data)

# Tạo cửa sổ GUI
root = tk.Tk()
root.title("Hiển thị dữ liệu SHT20")

# Tạo các LabelFrame để hiển thị dữ liệu
temperature_frame = ttk.LabelFrame(root, text="Nhiệt độ", padding=(10, 5))
temperature_frame.pack(padx=10, pady=10, fill="both", expand=True)

humidity_frame = ttk.LabelFrame(root, text="Độ ẩm", padding=(10, 5))
humidity_frame.pack(padx=10, pady=10, fill="both", expand=True)

data_frame = ttk.LabelFrame(root, text="Dữ liệu nhận được", padding=(10, 5))
data_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Cấu hình font cho các nhãn hiển thị
font_config = ("Helvetica", 40)

# Tạo các nhãn để hiển thị dữ liệu
temperature_label = ttk.Label(temperature_frame, text="Nhiệt độ: ", font=font_config)
temperature_label.pack(pady=10)

humidity_label = ttk.Label(humidity_frame, text="Độ ẩm: ", font=font_config)
humidity_label.pack(pady=10)

data_label = ttk.Label(data_frame, text="Dữ liệu nhận được: ", font=font_config)
data_label.pack(pady=10)

# Bắt đầu cập nhật dữ liệu
update_data()

# Chạy vòng lặp GUI
root.mainloop()
