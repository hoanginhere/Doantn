import os
import paho.mqtt.client as mqtt
from ftplib import FTP
import datetime

FTP_HOST = None
FTP_USERNAME = None
FTP_PASSWORD = None
last_sent_date = None

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("ftp/config")

def send_file_daily(city, factory, station):
    global last_sent_date, FTP_HOST, FTP_USERNAME, FTP_PASSWORD
    current_date = datetime.date.today()
    yesterday = current_date - datetime.timedelta(days=1)

    if last_sent_date != yesterday:
        print(f"Sending file for {yesterday} to FTP server for {city}, {factory}, {station}...")
        last_sent_date = yesterday
        # FTP client setup
        if FTP_HOST and FTP_USERNAME and FTP_PASSWORD:
            ftp = FTP(FTP_HOST)
            ftp.login(FTP_USERNAME, FTP_PASSWORD)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(script_dir, 'data_output')

            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    local_file = os.path.join(data_dir, filename)
                    remote_file = f"{city}_{factory}_{station}_{filename}"
                    with open(local_file, 'rb') as f:
                        ftp.storbinary(f'STOR {remote_file}', f)
                    print(f"File '{remote_file}' uploaded to FTP server successfully.")
            ftp.quit()
    else:
        print(f"File for {yesterday} already sent.")

def on_message(client, userdata, msg):
    global FTP_HOST, FTP_USERNAME, FTP_PASSWORD
    # Parse the MQTT message to get the FTP connection details
    config = msg.payload.decode().split(",")
    city = None
    factory = None
    station = None
    for item in config:
        key, value = item.split(":")
        if key.strip() == "City":
            city = value.strip()
        elif key.strip() == "Factory":
            factory = value.strip()
        elif key.strip() == "Station":
            station = value.strip()
        elif key.strip() == "Host":
            FTP_HOST = value.strip()
        elif key.strip() == "Username":
            FTP_USERNAME = value.strip()
        elif key.strip() == "Password":
            FTP_PASSWORD = value.strip()

    print(f"Received FTP config: {FTP_HOST}, {FTP_USERNAME}, {FTP_PASSWORD}")

    # Check if all required variables are set
    if city is not None and factory is not None and station is not None:
        # After receiving FTP config, send file daily
        send_file_daily(city, factory, station)
    else:
        print("Incomplete FTP config received. Unable to send file.")

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()
