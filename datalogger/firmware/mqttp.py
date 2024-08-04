import paho.mqtt.client as mqtt


# Cấu hình proxy
proxy_host = "26.26.26.1"
proxy_port = 10809


def main():
    client = mqtt.Client()

    # Thiết lập proxy
# Thiết lập proxy
    client.username_pw_set(proxy_host, proxy_port)
    # Thiết lập SSL/TLS (tùy chọn)

    # Kết nối đến máy chủ MQTT
    client.connect("broker.emqx.io", 1883)

    # Gửi tin nhắn
    client.publish("my/topic", "Hello, world!")

    # Ngắt kết nối
    client.disconnect()

if __name__ == "__main__":
    main()