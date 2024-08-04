import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# Thông tin kết nối MQTT
broker = 'localhost'
port = 1883
topic_sensor1 = 'sensor/1'
topic_sensor2 = 'sensor/2'
topic_sensor3 = 'sensor/3'
topic_sensor4 = 'sensor/4'
topic_sensor5 = 'sensor/5'
topic_sensor6 = 'sensor/6'
topic_sensor7 = 'sensor/7'
topic_sensor8 = 'sensor/8'

# Hàm callback khi kết nối tới broker thành công
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Đã kết nối tới MQTT broker với mã kết quả {rc}")
    else:
        print(f"Không thể kết nối tới MQTT broker với mã kết quả {rc}")

# Tạo đối tượng MQTT client
client = mqtt.Client()

# Gán hàm callback cho sự kiện kết nối
client.on_connect = on_connect

# Kết nối tới MQTT broker
client.connect(broker, port, 60)

# Bắt đầu vòng lặp sự kiện MQTT để xử lý kết nối và gửi tin nhắn
client.loop_start()

try:
    while True:
        # Gửi dữ liệu từ các cảm biến
        for sensor_id in range(1, 9):
            sensor_data = {
                'sensor{}'.format(sensor_id): {
                    'timestamp': datetime.utcnow().isoformat() + "Z",
                    'name': 'Sensor {}'.format(sensor_id),
                    'value': round(random.uniform(20.0, 30.0), 2),
                    'unit': round(random.uniform(40.0, 70.0), 2)
                }
            }
            topic = 'sensor/{}'.format(sensor_id)
            client.publish(topic, json.dumps(sensor_data))
            print(f"Đã gửi tin nhắn cho {topic}: {json.dumps(sensor_data)}")

        # Đợi một chút trước khi gửi tin nhắn tiếp theo
        time.sleep(3)  # Gửi tin nhắn mỗi 3 giây
except KeyboardInterrupt:
    print("Dừng gửi tin nhắn.")

# Dừng vòng lặp sự kiện và ngắt kết nối
client.loop_stop()
client.disconnect()