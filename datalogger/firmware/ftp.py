import os
import paho.mqtt.client as mqtt
from ftplib import FTP
FTP_HOST = None
FTP_USERNAME = None
FTP_PASSWORD = None
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("ftp/config")
def on_message(client, userdata, msg):
    global FTP_HOST, FTP_USERNAME, FTP_PASSWORD
    # Parse the MQTT message to get the FTP connection details
    config = msg.payload.decode().split(",")
    for item in config:
        key, value = item.split(":")
        if key == "FTP_HOST":
            FTP_HOST = value
        elif key == "FTP_USERNAME":
            FTP_USERNAME = value
        elif key == "FTP_PASSWORD":
            FTP_PASSWORD = value
    print(f"Received FTP config: {FTP_HOST}, {FTP_USERNAME}, {FTP_PASSWORD}")
    # Now you can use the FTP connection details to upload files
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USERNAME, FTP_PASSWORD)
    # Get the path to the 'data' directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
        # Loop through all files in the 'data' directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            local_file = os.path.join(data_dir, filename)
            remote_file = filename
            with open(local_file, 'rb') as f:
                ftp.storbinary(f'STOR {remote_file}', f)
            print(f"File '{remote_file}' uploaded to FTP server successfully.")
        ftp.quit()
# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()