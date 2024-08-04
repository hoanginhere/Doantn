import time
import paho.mqtt.client as mqtt
import sqlite3
import threading
import csv
import json
import os
import random
import logging
from datetime import datetime
import serial

# Cấu hình ghi log
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Cấu hình MQTT broker
broker = "localhost"
port = 1883

# Cấu hình các cảm biến
sensor_configs = [
    {"name": "sensor1", "min_value": 5, "max_value": 100, "min_alarm": 1, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []},
    {"name": "sensor2", "min_value": 5, "max_value": 100, "min_alarm": 0, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []},
    {"name": "sensor3", "min_value": 1, "max_value": 2, "min_alarm": 0, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []},
    {"name": "sensor4", "min_value": 5, "max_value": 100, "min_alarm": 0, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []},
    {"name": "sensor5", "min_value": 5, "max_value": 100, "min_alarm": 0, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []},
    {"name": "sensor6", "min_value": 5, "max_value": 100, "min_alarm": 0, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []},
    {"name": "sensor7", "min_value": 5, "max_value": 100, "min_alarm": 0, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []},
    {"name": "sensor8", "min_value": 5, "max_value": 100, "min_alarm": 0, "max_alarm": 0, "status": 0, "unit": 0, "data_received_flag": False, "configured": False, "start_time": None, "run_hours": None, "data": []}
]

# Cấu hình RS485
rs485_config = {
    "port": '/dev/ttyUSB0',  # Cập nhật port RS485 của bạn
    "baudrate": 9600,  # Cập nhật baudrate của bạn
    "unit_id": 1,
    "start_address": 0,
    "configured": False,
    "data": []
}

# Hàm đọc ngẫu nhiên giá trị từ ADC (giả lập)
def read_adc(channel):
    try:
        data = random.randint(1020, 1030)
        time.sleep(2)
        return data
    except Exception as e:
        log_error("ADC error", "Firmware-read_adc Function", str(e))
        logging.error(f"Error reading ADC: {e}")
        return None

# Hàm đọc dữ liệu từ RS485
def read_rs485():
    try:
        ser = serial.Serial(rs485_config["port"], rs485_config["baudrate"], timeout=1)
        time.sleep(2)  # Chờ cổng serial ổn định
        ser.write(b'READ')  # Gửi lệnh READ
        time.sleep(1)
        data = ser.read(14)  # Đọc đúng 14 byte dữ liệu
        ser.close()
        if data:
            logging.debug(f"Đọc RS485: {data}")
            return data.decode(errors='ignore')  # Bỏ qua lỗi giải mã
        else:
            error_message = "No receive data"
            log_error("RS485 error", "Firmware-read_rs485 Function", error_message)
            logging.error(error_message)
            return None
    except Exception as e:
        log_error("RS485 error", "Firmware-read_rs485 Function", str(e))
        logging.error(f"Lỗi đọc RS485: {e}")
        return None

# Hàm xử lý dữ liệu từ cảm biến
def process_data(raw_value, sensor_config):
    try:
        min_value = float(sensor_config["min_value"])
        max_value = float(sensor_config["max_value"])
        processed_value = raw_value * (max_value - min_value) / 4096 + min_value
        return processed_value
    except Exception as e:
        log_error("Processing error", "Firmware-process_data Function", str(e))
        logging.error(f"Error processing data: {e}")
        return None

# Hàm xử lý dữ liệu nhận được từ RS485
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
            error_message = "Incorrect data format"
            log_error("RS485 error", "Firmware-extract_data Function", error_message)
            logging.error(error_message)
            return None, None
    except Exception as e:
        log_error("RS485 error", "Firmware-extract_data Function", str(e))
        logging.error(f"Error extracting data: {e}")
        return None, None

# Hàm lưu lỗi vào SQLite
def log_error(error_type, location, description):
    conn = sqlite3.connect("/home/hp/Doantn/Firmware/data.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS app_error (Timestamp TEXT, Type TEXT, Location TEXT, Describe TEXT)")
    timestamp_str = datetime.now().isoformat()
    cursor.execute("INSERT INTO app_error (Timestamp, Type, Location, Describe) VALUES (?, ?, ?, ?)", (timestamp_str, error_type, location, description))
    conn.commit()
    conn.close()

# Hàm chung lưu dữ liệu vào SQLite
def save_to_sqlite(table_name, name, timestamp, unit, value):
    try:
        conn = sqlite3.connect("/home/hp/Doantn/Firmware/data.db")
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (name TEXT, timestamp TEXT, unit TEXT, value REAL)")
        timestamp_str = datetime.fromtimestamp(timestamp).isoformat()
        cursor.execute(f"INSERT INTO {table_name} (name, timestamp, unit, value) VALUES (?, ?, ?, ?)", (name, timestamp_str, unit, value))
        conn.commit()
        conn.close()
    except Exception as e:
        log_error("Database error", "Firmware-save_to_sqlite Function", str(e))
        logging.error(f"Error saving to SQLite: {e}")

# Hàm chung lưu dữ liệu vào CSV
def save_to_csv(file_name, port, timestamp, value, unit, output_dir):
    try:
        date_str = time.strftime("%Y-%m-%d", time.localtime(timestamp))
        file_path = os.path.join(output_dir, f"{file_name}_{date_str}.csv")
        file_exists = os.path.isfile(file_path)
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["port", "timestamp", "value", "unit"])
            writer.writerow([port, datetime.fromtimestamp(timestamp).isoformat(), value, unit])
    except Exception as e:
        log_error("CSV error", "Firmware-save_to_csv Function", str(e))
        logging.error(f"Error saving to CSV: {e}")

# Hàm gửi dữ liệu qua MQTT
def send_data_mqtt(client, name, value, unit, port):
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        message = {
            "timestamp": timestamp,
            "name": name,
            "value": value,
            "unit": unit
        }
        topic = f"sensor/{port}"
        client.publish(topic, json.dumps(message))
        logging.debug(f"Data sent to MQTT: Topic: {topic}, Message: {message}")
    except Exception as e:
        log_error("MQTT error", "Firmware-send_data_mqtt Function", str(e))
        logging.error(f"Error sending data to MQTT: {e}")

# Hàm xử lý tin nhắn MQTT cho các cảm biến
def on_message_sensor(client, userdata, msg, sensor_index):
    try:
        data = json.loads(msg.payload.decode())
        sensor_configs[sensor_index]["name"] = data.get("Name", sensor_configs[sensor_index]["name"])
        sensor_configs[sensor_index]["min_value"] = data.get("Min_Value", sensor_configs[sensor_index]["min_value"])
        sensor_configs[sensor_index]["max_value"] = data.get("Max_Value", sensor_configs[sensor_index]["max_value"])
        sensor_configs[sensor_index]["min_alarm"] = data.get("Min_Alarm", sensor_configs[sensor_index]["min_alarm"])
        sensor_configs[sensor_index]["max_alarm"] = data.get("Max_Alarm", sensor_configs[sensor_index]["max_alarm"])
        sensor_configs[sensor_index]["status"] = data.get("Status", sensor_configs[sensor_index]["status"])
        sensor_configs[sensor_index]["unit"] = data.get("Unit", sensor_configs[sensor_index]["unit"])
        sensor_configs[sensor_index]["data_received_flag"] = True
        sensor_configs[sensor_index]["configured"] = True
        logging.debug(f"Sensor {sensor_index} configuration updated with data: {data}")
    except Exception as e:
        log_error("MQTT error", "Firmware-on_message_sensor Function", str(e))
        logging.error(f"Error processing MQTT message for sensor {sensor_index}: {e}")

# Hàm xử lý tin nhắn MQTT cho thời gian
def on_message_time(client, userdata, msg, sensor_index):
    try:
        data = json.loads(msg.payload.decode())
        sensor_configs[sensor_index]["start_time"] = data.get("start_time", sensor_configs[sensor_index]["start_time"])
        sensor_configs[sensor_index]["run_hours"] = data.get("run_hours", sensor_configs[sensor_index]["run_hours"])
        sensor_configs[sensor_index]["data_received_flag"] = True
        logging.debug(f"Sensor {sensor_index} time configuration updated with data: {data}")
    except Exception as e:
        log_error("MQTT error", "Firmware-on_message_time Function", str(e))
        logging.error(f"Error processing MQTT time message for sensor {sensor_index}: {e}")

# Hàm xử lý tin nhắn MQTT cho RS485
def on_message_rs485(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rs485_config["port"] = data.get("Port", rs485_config["port"])
        rs485_config["baudrate"] = data.get("Baudrate", rs485_config["baudrate"])
        rs485_config["unit_id"] = data.get("Unit_ID", rs485_config["unit_id"])
        rs485_config["start_address"] = data.get("Start_Address", rs485_config["start_address"])
        rs485_config["configured"] = True
        logging.debug(f"RS485 configuration updated with data: {data}")
    except Exception as e:
        log_error("MQTT error", "Firmware-on_message_rs485 Function", str(e))
        logging.error(f"Error processing MQTT message for RS485: {e}")

# Hàm lắng nghe MQTT cho cảm biến
def mqtt_listener(sensor_index, port):
    try:
        client = mqtt.Client()
        client.connect(broker, port)

        topic = f"config/port{sensor_index + 1}"
        client.message_callback_add(topic, lambda client, userdata, msg: on_message_sensor(client, userdata, msg, sensor_index))
        client.subscribe(topic)

        topic_time = f"time/port{sensor_index + 1}"
        client.message_callback_add(topic_time, lambda client, userdata, msg: on_message_time(client, userdata, msg, sensor_index))
        client.subscribe(topic_time)

        client.loop_forever()
    except Exception as e:
        log_error("MQTT error", "Firmware-mqtt_listener Function", str(e))
        logging.error(f"Error in MQTT listener for sensor {sensor_index}: {e}")

# Hàm nghe MQTT cho RS485
def mqtt_listener_rs485(port):
    try:
        client = mqtt.Client()
        client.connect(broker, port)

        topic = "config/rs485"
        client.message_callback_add(topic, on_message_rs485)
        client.subscribe(topic)

        client.loop_forever()
    except Exception as e:
        log_error("MQTT error", "Firmware-mqtt_listener_rs485 Function", str(e))
        logging.error(f"Error in MQTT listener for RS485: {e}")

# Hàm xử lý dữ liệu cho các cổng ADC
def process_sensor(sensor_index):
    try:
        client = mqtt.Client()
        client.connect(broker, port)
        start_time = time.time()
        first_last_values = []

        while True:
            if sensor_configs[sensor_index]["configured"] and sensor_configs[sensor_index]["data_received_flag"]:
                raw_value = read_adc(sensor_index)
                if raw_value is None:
                    continue  # Bỏ qua nếu không nhận được giá trị
                processed_value = process_data(raw_value, sensor_configs[sensor_index])
                if processed_value is None:
                    continue  # Bỏ qua nếu không xử lý được giá trị
                current_time = time.time()
                elapsed_time = current_time - start_time
                sensor_configs[sensor_index]["data"].append(processed_value)

                # Gửi dữ liệu đọc qua MQTT 2 giây một lần
                if len(sensor_configs[sensor_index]["data"]) % 2 == 0:
                    send_data_mqtt(client, sensor_configs[sensor_index]["name"], processed_value, sensor_configs[sensor_index]["unit"], sensor_index + 1)
                    logging.debug(f"Đã gửi tin nhắn tới sensor/{sensor_index+1}")

                # Lưu dữ liệu vào cơ sở dữ liệu và file CSV mỗi 60 giây
                if elapsed_time >= 60:
                    table_name = f"app_sensor{sensor_index + 1}"
                    if len(first_last_values) == 2:
                        k = (first_last_values[0] + first_last_values[1]) / 2
                        min_value = 0.95 * k
                        max_value = 1.05 * k
                        within_range = all(min_value <= value <= max_value for value in first_last_values)

                        if within_range:
                            save_to_sqlite(table_name, sensor_configs[sensor_index]["name"], current_time, sensor_configs[sensor_index]["unit"], k)
                            save_to_csv("Data", f"port_{sensor_index + 1}", current_time, k, sensor_configs[sensor_index]["unit"], "/home/hp/Doantn/Firmware/data_output")
                        else:
                            if any(value < sensor_configs[sensor_index]["min_alarm"] or value > sensor_configs[sensor_index]["max_alarm"] for value in first_last_values):
                                save_to_sqlite("Alarm", sensor_configs[sensor_index]["name"], current_time, sensor_configs[sensor_index]["unit"], k)
                                save_to_csv("Alarm", f"port_{sensor_index + 1}", current_time, k, sensor_configs[sensor_index]["unit"], "/home/hp/Doantn/Firmware/data_output")
                            else:
                                save_to_sqlite(table_name, sensor_configs[sensor_index]["name"], current_time, sensor_configs[sensor_index]["unit"], k)
                                save_to_csv("Data", f"port_{sensor_index + 1}", current_time, k, sensor_configs[sensor_index]["unit"], "/home/hp/Doantn/Firmware/data_output")

                        first_last_values = [processed_value]
                        start_time = current_time
                    else:
                        first_last_values.append(processed_value)
                else:
                    if len(first_last_values) < 2:
                        first_last_values.append(processed_value)
                time.sleep(0.5)
    except Exception as e:
        log_error("Processing error", "Firmware-process_sensor Function", str(e))
        logging.error(f"Error in process_sensor for sensor {sensor_index}: {e}")

# Hàm xử lý dữ liệu cho RS485
def process_sensor_rs485():
    try:
        client = mqtt.Client()
        client.connect(broker, port)
        start_time = time.time()
        first_last_values = []

        while True:
            if rs485_config["configured"]:
                raw_value = read_rs485()
                if raw_value is None:
                    continue  # Bỏ qua nếu không nhận được dữ liệu
                temperature, _ = extract_data(raw_value)
                if temperature is None:
                    continue  # Bỏ qua nếu không thể tách dữ liệu
                processed_value = process_data(float(temperature), rs485_config)
                if processed_value is None:
                    continue  # Bỏ qua nếu không xử lý được giá trị
                current_time = time.time()
                elapsed_time = current_time - start_time
                rs485_config["data"].append(processed_value)

                # Gửi dữ liệu đọc qua MQTT 2 giây một lần
                if len(rs485_config["data"]) % 2 == 0:
                    send_data_mqtt(client, "rs485_sensor", processed_value, "unit", "rs485")
                    logging.debug(f"Đã gửi tin nhắn tới sensor/rs485")

                # Lưu dữ liệu vào cơ sở dữ liệu và file CSV mỗi 60 giây
                if elapsed_time >= 60:
                    table_name = "app_sensor_rs485"
                    if len(first_last_values) == 2:
                        k = (first_last_values[0] + first_last_values[1]) / 2
                        min_value = 0.95 * k
                        max_value = 1.05 * k
                        within_range = all(min_value <= value <= max_value for value in first_last_values)

                        if within_range:
                            save_to_sqlite(table_name, "rs485_sensor", current_time, "unit", k)
                            save_to_csv("Data", "rs485", current_time, k, "unit", "/home/hp/Doantn/Firmware/data_output")
                        else:
                            if any(value < rs485_config["min_alarm"] or value > rs485_config["max_alarm"] for value in first_last_values):
                                save_to_sqlite("Alarm", "rs485_sensor", current_time, "unit", k)
                                save_to_csv("Alarm", "rs485", current_time, k, "unit", "/home/hp/Doantn/Firmware/data_output")
                            else:
                                save_to_sqlite(table_name, "rs485_sensor", current_time, "unit", k)
                                save_to_csv("Data", "rs485", current_time, k, "unit", "/home/hp/Doantn/Firmware/data_output")

                        first_last_values = [processed_value]
                        start_time = current_time
                    else:
                        first_last_values.append(processed_value)
                else:
                    if len(first_last_values) < 2:
                        first_last_values.append(processed_value)
                time.sleep(0.5)
    except Exception as e:
        log_error("Processing error", "Firmware-process_sensor_rs485 Function", str(e))
        logging.error(f"Error in process_sensor_rs485: {e}")

# Khởi tạo các thread cho các cổng ADC và RS485
def start_threads():
    try:
        threads = []
        for i in range(8):
            t = threading.Thread(target=mqtt_listener, args=(i, port))
            threads.append(t)
            t = threading.Thread(target=process_sensor, args=(i,))
            threads.append(t)

        t = threading.Thread(target=mqtt_listener_rs485, args=(port,))
        threads.append(t)
        t = threading.Thread(target=process_sensor_rs485)
        threads.append(t)

        for t in threads:
            t.start()
    except Exception as e:
        log_error("Thread error", "Firmware-start_threads Function", str(e))
        logging.error(f"Error starting threads: {e}")

# Bắt đầu các thread
if __name__ == "__main__":
    start_threads()
