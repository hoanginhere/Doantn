import paho.mqtt.client as mqtt
import json
import time

# Cấu hình MQTT broker
broker = "broker.emqx.io"
port = 1883

# Tạo client MQTT
client = mqtt.Client()
client.connect(broker, port)

# Dữ liệu cài đặt thời gian cho sensor1
time_data = {
    "Start_Time": "2024-06-16T10:40:00",
    "Run_Hours": 8
}

# Gửi dữ liệu liên tục với khoảng thời gian 2 giây
while True:
    # Chuyển đổi thành JSON và gửi
    topic = "time/port1"
    client.publish(topic, json.dumps(time_data))
    print("Đã gửi dữ liệu lên MQTT broker.")

    # Nghỉ 2 giây trước khi gửi lại
    time.sleep(2)
    