import random
import paho.mqtt.client as mqtt
import json
import serial
import time
import datetime
import sqlite3
import os
import ftplib
from ftplib import FTP
import spidev
import time
import socket
import openpyxl
#import RPi.GPIO as GPIO
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
#LẤY ĐỊA CHỈ IPv4
def get_ipv4_address():
    try:
        # Tạo một socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Kết nối socket đến một địa chỉ IP và port tạm thời
        s.connect(("8.8.8.8", 80))
        # Lấy địa chỉ IP của máy tính
        ip_address = s.getsockname()[0]
        # Đóng socket
        s.close()
        return ip_address
    except socket.error as e:
        print(f"Error: {e}")
        return None

# ĐỌC CẢM BIẾN RS485 BẰNG MODBUS (1 Sensor)
def readData_RS485(port, baud, typed, address, id):
    try:
        client = ModbusClient(method='rtu', port=port,
                             baudrate=baud, timeout=1, parity='N',
                             strict=False, stopbits=1)
        client.connect()
        time.sleep(1)
        if typed == "signed":
            response = client.read_input_registers(int(address), count=1,
                                                  unit=int(id))
            # a = response.registers
            # k = round(a[0]/100,2)
            client.close()
            return response
        if typed == "float":
            response = client.read_input_registers(int(address), 2,
                                                  unit=int(id))
            value1 = response.registers[0]
            value2 = response.registers[1]
            value = [value1, value2]
            decoder = BinaryPayloadDecoder.fromRegisters(value,
                                                        byteorder=Endian.Big)
            p = decoder.decode_32bit_float()
            m = round(p, 3)
            client.close()
            return m
    except ModbusIOException as e:
        print(f'Modbus Error: {e}')
        # print('Cannot read Sensor RS485')

# ĐỌC CẢM BIẾN 4-20mA (4 Sensor)
GPIO.setmode(GPIO.BCM)
SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
# The chip select pin is connected to GPIO 12
CS_ADC = 12
GPIO.setup(CS_ADC, GPIO.OUT)

# Read adc value
def readData_Analog(channel, Enable, M, m):
    try:
        adc = spi.xfer2([4 | 2 | (channel >> 2), (channel & 3) << 6, 0])
        data_analog = ((adc[1] & 15) << 8) + adc[2]
        if Enable == False or Enable == None:
            return data_analog
        else:
            real_data = ((M-m)/4095)*data_analog + m
            return real_data
    except:
        print('Cannot read Analog Sensor')

# ĐỌC CẢM BIẾN DIGITAL (4 Sensor)
def read_sensor_digital(Enable, M, m, DIGITAL_PIN):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DIGITAL_PIN, GPIO.IN)
        sensor_value = GPIO.input(DIGITAL_PIN)
        time.sleep(1)
        if Enable == False or Enable == None:
            return sensor_value
        else:
            real_data = ((M-m)/4095)*sensor_value + m
            return real_data
    except KeyboardInterrupt:
        GPIO.cleanup()

# GỬI DỮ LIỆU CẢM BIẾN LÊN GIAO DIỆN
# Cài đặt thông tin MQTT broker (Mosquitto)
broker_address = str(get_ipv4_address())  # Điền địa chỉ MQTT broker của bạn
port = 1883  # Port mặc định của MQTT broker
client = mqtt.Client()
#ĐỌC DỮ LIỆU TỪ TOPIC TRÊN MQTT MÀ NODE-RED ĐÃ GỬI LÊN (SETTINGS)
def subscribe(topic):
    try:
        global client, broker_address
        def on_message(client, userdata, msg):
            global received_data
            received_data = msg.payload.decode('utf-8')
            # print(f"Received message on topic {msg.topic}: {received_data}")

        # Set the message handling function
        client.on_message = on_message

        # Connect to the MQTT broker
        client.connect("127.0.0.1", 1883, 60)

        # Subscribe to a specific topic
        client.subscribe(topic)

        start_time = time.time()
        while time.time() - start_time < 2:
            client.loop(timeout=1)

        # print("Final received data " + str(topic), received_data)
        client.disconnect()
        client.loop_stop()
        return received_data
    except:
        print("Cannot subscribe topic in mqtt")

def sendData_to_nodeRED(Data_1, Data_2, Data_3, Data_4, Data_5, Data_6, Data_7, Data_8, Data_9):
    try:
        # JSON data you want to send
        data = {
            "Port_1": Data_1,
            "Port_2": Data_2,
            "Port_3": Data_3,
            "Port_4": Data_4,
            "Port_5": Data_5,
            "Port_6": Data_6,
            "Port_7": Data_7,
            "Port_8": Data_8,
            "Port_9": Data_9
        }

        # Convert data to JSON string
        json_data = json.dumps(data)

        # MQTT topic identifier
        # Connect to MQTT Broker
        client.connect("127.0.0.1", 1883)

        # Publish JSON data to MQTT broker
        client.publish('datalogger/value', json_data)
        print("Send data to nodeRED - Success")

        # Disconnect after sending data
        client.disconnect()
    except:
        print('Cannot send data to nodeRED')

def connect_database():
    global connection, cursor
    try:
        global real_datetime, real_time, real_date
        connection = sqlite3.connect('Database.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        # PARSE_DECLTYPES allows SQLite to parse declared types in the SQLite database, 
        # such as DATE, TIMESTAMP, etc.
        # PARSE_COLNAMES allows SQLite to parse column names in the SQLite database.
        cursor = connection.cursor()
    except:
        print("Cannot connect to Database.db")

def create_table():
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS database (
            Date TEXT,
            Time TEXT,
            Port_1 null,
            Port_2 null,
            Port_3 null,
            Port_4 null,
            Port_5 null,
            Port_6 null,
            Port_7 null,
            Port_8 null,
            Port_9 null
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS alarm (
            Date TEXT,
            Time TEXT,
            Name null,
            Value null
        )""")
    except:
        print("Cannot create data and alarm table")

def write_data_to_database(Save_1, Save_2, Save_3, Save_4, Save_5, Save_6, Save_7, Save_8,
                          Save_9):  # Ghi giá trị cảm biến vào database
    try:
        real_datetime = datetime.datetime.now()
        real_time = str(real_datetime.strftime("%X"))
        real_date = str(real_datetime.strftime("%x"))
        cursor.execute("""INSERT INTO database(Date, Time, Port_1, Port_2, Port_3, Port_4, Port_5,
                       Port_6, Port_7, Port_8, Port_9) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                      (real_date, real_time, Save_1, Save_2, Save_3, Save_4, Save_5, Save_6, Save_7, Save_8, Save_9))
        connection.commit()
        cursor.execute("SELECT * FROM database")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except:
        print('Cannot write data sensor to database')

# LƯU DỮ LIỆU DẠNG TEXT VÀO FOLDER THÍCH HỢP TRÊN RASPBERRY PI
def create_folder(name):  # Kiểm tra folder tồn tại hay không và tạo folder
    # try:
    global real_datetime
    real_datetime = datetime.datetime.now()
    global real_time
    real_time = real_datetime.strftime("%X")
    global real_date
    real_date = real_datetime.strftime("%x")
    if os.path.exists("/home/datalogger/iPACLAB/data/" + name) == False:
        os.mkdir("/home/datalogger/iPACLAB/data/" + name)
    if os.path.exists("/home/datalogger/iPACLAB/data/" + name + "/20" + real_date[6:8]) == False:
        os.mkdir("/home/datalogger/iPACLAB/data/" + name + "/20" + real_date[6:8])
    if os.path.exists("/home/datalogger/iPACLAB/data/" + name + "/20" + real_date[6:8] + "/" +
                     real_date[0:2]) == False:
        os.mkdir("/home/datalogger/iPACLAB/data/" + name + "/20" + real_date[6:8] + "/" +
                 real_date[0:2])
    if os.path.exists("/home/datalogger/iPACLAB/data/" + name + "/20" + real_date[6:8] + "/" +
                     real_date[0:2] + "/" + real_date[3:5]) == False:
        os.mkdir("/home/datalogger/iPACLAB/data/" + name + "/20" + real_date[6:8] + "/" +
                 real_date[0:2] + "/" + real_date[3:5])
    # except:
    #print("Cannot create folder")

def createFile(name, City, Factory, Station):
    global path, r_datetime, filename, real_path
    try:
        real_datetime = datetime.datetime.now()
        real_time = real_datetime.strftime("%X")
        real_date = real_datetime.strftime("%x")
        path = "/home/datalogger/iPACLAB/data/"+ name + "/20" + real_date[6:8] + "/" + real_date[0:2] \
              + "/" + real_date[3:5]
        r_datetime = '20' + real_date[6:8] + real_date[0:2] + real_date[3:5] + real_time[0:2] + \
                     real_time[3:5] + "00"

        filename = os.path.join(path + "/" + str(City) + "_" + str(Factory) + "_" + str(Station) + "_" +
                               r_datetime + '.txt')
        real_path = path + "/" + str(City) + "_" + str(Factory) + "_" + str(Station) + "_" + r_datetime + \
                    '.txt'
        file = open(filename,"w")
        file.close()
    except:
        print("Cannot create text file")

def write_data_to_text(name, Value_1, Value_2, Value_3, Value_4, Value_5, Value_6, Value_7,
                      Value_8, Value_9, Unit_1, Unit_2, Unit_3, Unit_4, Unit_5, Unit_6, Unit_7, Unit_8, Unit_9,
                      Status_1, Status_2, Status_3, Status_4, Status_5, Status_6, Status_7, Status_8, Status_9, City,
                      Factory, Station):
    try:
        read_date_and_time = '20' + real_date[6:8] + real_date[0:2] + real_date[3:5] + real_time[0:2] + \
                             real_time[3:5] + "00"
        content = 'Port_1' + '\t' + str(Value_1) + '\t' + str(Unit_1) + '\t' + read_date_and_time + '\t' + \
                  str(Status_1) + '\n' + 'Port_2' + '\t' + str(Value_2) + '\t' + str(Unit_2) + '\t' + read_date_and_time + \
                  '\t' + str(Status_2) + '\n' + 'Port_3' + '\t' + str(Value_3) + '\t' + str(Unit_3) + '\t' + \
                  read_date_and_time + '\t' + str(Status_3) + '\n' + 'Port_4' + '\t' + str(Value_4) + '\t' + str(Unit_4) + \
                  '\t' + read_date_and_time + '\t' + str(Status_4) + '\n' + 'Port_5' + '\t' + str(Value_5) + '\t' + \
                  str(Unit_5) + '\t' + read_date_and_time + '\t' + str(Status_5) + '\n' + 'Port_6' + '\t' + str(Value_6) + \
                  '\t' + str(Unit_6) + '\t' + read_date_and_time + '\t' + str(Status_6) + '\n' + 'Port_7' + '\t' + \
                  str(Value_7) + '\t' + str(Unit_7) + '\t' + read_date_and_time + '\t' + str(Status_7) + '\n' + 'Port_8' + \
                  '\t' + str(Value_8) + '\t' + str(Unit_8) + '\t' + read_date_and_time + '\t' + str(Status_8) + '\n' + \
                  'Port_9' + '\t' + str(Value_9) + '\t' + str(Unit_9) +'\t'+ read_date_and_time + '\t' + str(Status_9) + \
                  '\n'
        filename = "/home/datalogger/iPACLAB/data/" + "/" + name + "/" + "20" + real_date[6:8] + "/" \
                   + real_date[0:2] + "/" + real_date[3:5] + "/" + str(City) + "_" + str(Factory) + "_" + str(Station) + \
                   "_" + read_date_and_time + ".txt"
        file = open(filename,'w')
        file.write(content)
        file.close()
        print (content)
    except:
        print("Cannot write data to text file")
#TRUYỀN DỮ LIỆU VÀO FTP SERVER QUA GIAO THỨC FTP
def connect(ftpHost, ftpUname, ftpPass):
    try:
        global ftp
        ftp = ftplib.FTP(ftpHost, ftpUname, ftpPass)
        ftp.encoding = "utf-8"
        ftp = FTP(ftpHost)
        ftp.login(ftpUname, ftpPass)
    except:
        print("Cannot connect to FTP Server")

def createFolderFTP(name):
    real_datetime = datetime.datetime.now()
    real_date = real_datetime.strftime("%x")
    try:
        bool0 = name in ftp.nlst()
        if bool0 == True:
            ftp.cwd(name)
            print("Thư mục " + name + " đã tồn tại trên Server")
        if bool0 == False:
            ftp.mkd(name)
            ftp.cwd(name)
            print("Thư mục " + name + "chưa tồn tại trên Server")

        folderName1 = "20" + real_date[6:8]
        folder1 = ftp.nlst()
        if folder1 != []:
            for c in folder1:
                if c == folderName1:
                    bool1 = True
                    break
                else:
                    bool1 = False
        else:
            bool1 = False

        if bool1 == True:
            ftp.cwd("20" + real_date[6:8])
            print("Thư mục 20" + real_date[6:8] + " đã tồn tại trên Server")
        if bool1 == False:
            ftp.mkd("20" + real_date[6:8])
            ftp.cwd("20" + real_date[6:8])
            print("Thư mục 20" + real_date[6:8] + " chưa tồn tại trên Server. Đã tạo thư mục 20" + real_date[6:8])

        folderName2 = real_date[0:2]
        folder2 = ftp.nlst()
        if folder2 != []:
            for c in folder2:
                if c == folderName2:
                    bool2 = True
                    break
                else:
                    bool2 = False
        else:
            bool2 = False

        if bool2 == True:
            ftp.cwd(real_date[0:2])
            print("Thư mục " + real_date[0:2] + " đã tồn tại trên Server")
        if bool2 == False:
            ftp.mkd(real_date[0:2])
            ftp.cwd(real_date[0:2])
            print("Thư mục " + real_date[0:2] + " chưa tồn tại trên Server. Đã tạo thư mục " + real_date[0:2])

        folderName3 = real_date[3:5]
        folder3 = ftp.nlst()
        if folder3 != []:
            for c in folder3:
                if c == folderName3:
                    bool3 = True
                    break
                else:
                    bool3 = False
        else:
            bool3 = False

        if bool3 == True:
            ftp.cwd(real_date[3:5])
            print("Thư mục " + str(real_date[3:5]) + " đã tồn tại trên Server")
        if bool3 == False:
            ftp.mkd(real_date[3:5])
            ftp.cwd(real_date[3:5])
            print("Thư mục " + str(real_date[3:5]) + " chưa tồn tại trên Server. Đã tạo thư mục " + str(real_date[3:5]))
        ftp.quit()
    except:
        print("Lỗi khi tạo Folder")

def uploadFileFTP(filesave):
    try:
        ftp.cwd('data')
        year = "20" + real_date[6:8]
        ftp.cwd(year)
        ftp.cwd(real_date[0:2])
        ftp.cwd(real_date[3:5])
        with open(filesave, "rb") as file:
            print(filesave)
            ftp.storbinary('STOR {}'.format(os.path.basename(filesave)), file, 1024*1024)
            print('uploadFileFTP success')
        ftp.quit()
    except:
        print("Cannot send file to FTP Server")

# TRUYỀN DỮ LIỆU EXCEL ĐẾN ĐỊA CHỈ EMAIL
def exportExcelFile(year_start, month_start, day_start, year_fin, month_fin, day_fin):
    try:
        book = openpyxl.Workbook()
        sheet = book.active
        start = str(month_start + "/" + day_start + "/" + year_start)
        print("Dữ liệu được trích xuất trong ngày " + start)
        finish = str(month_fin + "/" + day_fin + "/" + year_fin)
        cursor.execute('SELECT * FROM database WHERE date BETWEEN (?) AND (?)', (start, finish))
        d = cursor.fetchall()
        print(d)
        i = 0
        for row in d:
            sheet['A1'] = "Date"
            sheet['B1'] = "Time"
            sheet['C1'] = "Port_1"
            sheet['D1'] = "Port_2"
            sheet['E1'] = "Port_3"
            sheet['F1'] = "Port_4"
            sheet['G1'] = "Port_5"
            sheet['H1'] = "Port_6"
            sheet['I1'] = "Port_7"
            sheet['J1'] = "Port_8"
            sheet['K1'] = "Port_9"
            i += 1
            j = 1
            for col in row:
                cell = sheet.cell(row=i+1, column=j)
                cell.value = col
                j += 1
        fileExcel = "/home/datalogger/iPACLAB/excel/database.xlsx"
        book.save(fileExcel)
        return fileExcel
    except:
        print("Lỗi khi xuất file Excel")
def write_data_to_alarm_database(Sensor_Name, Value): # Ghi giá trị cảm biến vào database
    try:
        real_datetime = datetime.datetime.now()
        real_time = str(real_datetime.strftime("%X"))
        real_date = str(real_datetime.strftime("%x"))
        cursor.execute("""INSERT INTO alarm(Date,Time,Name,Value) VALUES (?,?,?,?)""",(real_date,real_time, Sensor_Name, Value))
        connection.commit()
        cursor.execute("SELECT * FROM alarm")
        rows = cursor.fetchall()
        # for row in rows:
        #     print(row)
    except:
        print('Cannot write data alarm to alarm_database')

def alarmFunction(Status, Sensor_Value, Sensor_Name, Min, Max):
    try:
        if str(Status) == "Not_Used" or str(Status) == "01":
            pass
        elif Sensor_Value < Min or Sensor_Value > Max:
            write_data_to_alarm_database(Sensor_Name, Sensor_Value)
            S = '02'
            Status = S
        else:
            S = '00'
            Status = S
        return Status
    except:
        print("Cannot use alarm Function")

# TEST
# global Sensor_1, Sensor_2, Sensor_3, Sensor_4, Sensor_5, Sensor_6, Sensor_7, Sensor_8
real_datetime = datetime.datetime.now()
global real_time, real_date
real_time = real_datetime.strftime("%X")
real_date = real_datetime.strftime("%x")

# TẠO VÀ CONNECT TỚI DATABASE
connect_database()
# TẠO BẢNG TRONG DATABASE
create_table()
# TẠO FOLDER THEO YÊU CẦU Ở PI
create_folder('data')

while 1:
    duration = 0
    t1 = time.time()
    # CẤU HÌNH CẢM BIẾN
    A0 = json.loads(subscribe("settings/sensor/analog/A0"))
    A1 = json.loads(subscribe("settings/sensor/analog/A1"))
    A2 = json.loads(subscribe("settings/sensor/analog/A2"))
    A3 = json.loads(subscribe("settings/sensor/analog/A3"))
    D0 = json.loads(subscribe("settings/sensor/digital/D0"))
    D1 = json.loads(subscribe("settings/sensor/digital/D1"))
    D2 = json.loads(subscribe("settings/sensor/digital/D2"))
    D3 = json.loads(subscribe("settings/sensor/digital/D3"))
    RS485 = json.loads(subscribe("settings/sensor/rs485"))

    # CẤU HÌNH FTPSERVER
    FTPSERVER = json.loads(subscribe("settings/ftpserver"))

    while(duration < 60):
        # ĐỌC CẢM BIẾN
        Sensor_1 = readData_Analog(A0["Status"], A0["Min_Value"], A0["Max_Value"])
        Sensor_2 = readData_Analog(A1["Status"], A1["Min_Value"], A1["Max_Value"])
        Sensor_3 = readData_Analog(A2["Status"], A2["Min_Value"], A2["Max_Value"])
        Sensor_4 = readData_Analog(A3["Status"], A3["Min_Value"], A3["Max_Value"])
        Sensor_5 = read_sensor_digital(D0["Status"], D0["Min_Value"], D0["Max_Value"], D0["GPIO"])
        Sensor_6 = read_sensor_digital(D1["Status"], D1["Min_Value"], D1["Max_Value"], D1["GPIO"])
        Sensor_7 = read_sensor_digital(D2["Status"], D2["Min_Value"], D2["Max_Value"], D2["GPIO"])
        Sensor_8 = read_sensor_digital(D3["Status"], D3["Min_Value"], D3["Max_Value"], D3["GPIO"])
        Sensor_9 = readData_RS485('/tty/AMA0', RS485["Baudrate"], RS485["Type"], RS485["ID"], RS485["Address"])

        # GỬI GIÁ TRỊ CẢM BIẾN LÊN GIAO DIỆN
        sendData_to_nodeRED(Sensor_1, Sensor_2, Sensor_3, Sensor_4, Sensor_5, Sensor_6, Sensor_7, Sensor_8, Sensor_9)

        # CẢNH BÁO VƯỢT DẢI ĐO
        Status_1 = alarmFunction(A0["Status"], Sensor_1, A0["Name"], A0["Min_Alarm"], A0["Max_Alarm"])
        Status_2 = alarmFunction(A1["Status"], Sensor_2, A1["Name"], A1["Min_Alarm"], A1["Max_Alarm"])
        Status_3 = alarmFunction(A2["Status"], Sensor_3, A2["Name"], A2["Min_Alarm"], A2["Max_Alarm"])
        Status_4 = alarmFunction(A3["Status"], Sensor_4, A3["Name"], A3["Min_Alarm"], A3["Max_Alarm"])
        Status_5 = alarmFunction(D0["Status"], Sensor_5, D0["Name"], D0["Min_Alarm"], D0["Max_Alarm"])
        Status_6 = alarmFunction(D1["Status"], Sensor_6, D1["Name"], D1["Min_Alarm"], D1["Max_Alarm"])
        Status_7 = alarmFunction(D2["Status"], Sensor_7, D2["Name"], D2["Min_Alarm"], D2["Max_Alarm"])
        Status_8 = alarmFunction(D3["Status"], Sensor_8, D3["Name"], D3["Min_Alarm"], D3["Max_Alarm"])
        Status_9 = alarmFunction(RS485["Status"], Sensor_9, RS485["Name"], RS485["Min_Alarm"], RS485["Max_Alarm"])

        # GỬI DỮ LIỆU EXCEL
        database_excel = json.loads(subscribe("database/excel"))
        if database_excel["Status"] == "on":
            exportExcelFile(year_start=str(24), month_start=str(real_date[0:2]), day_start=str(real_date[3:5]), year_fin=str(23), month_fin = str(real_date[0:2]), day_fin=str(real_date[3:5]))
        else:
            pass

        duration = time.time() - t1
        time.sleep(5)
        real_datetime = datetime.datetime.now()
        real_time = real_datetime.strftime("%X")
        real_date = real_datetime.strftime("%x")
        time1 = "20" + real_date[6:8] + "/" + real_date[0:2] + "/" + real_date[3:5]

        # TẠO FILE TEXT THEO YÊU CẦU
        createFile('data', FTPSERVER["City"], FTPSERVER["Factory"], FTPSERVER["Station"])

        # GHI NỘI DUNG VÀO FILE TEXT
        write_data_to_text('data', Sensor_1, Sensor_2, Sensor_3, Sensor_4, Sensor_5, Sensor_6,
                   Sensor_7, Sensor_8, Sensor_9, A0["Unit"], A1["Unit"], A2["Unit"], A3["Unit"],
                   D0["Unit"], D1["Unit"], D2["Unit"], D3["Unit"], RS485["Unit"], A0["Status"],
                   A1["Status"], A2["Status"], A3["Status"], D0["Status"], D1["Status"],
                   D2["Status"], D3["Status"], RS485["Status"], FTPSERVER["City"],
                   FTPSERVER["Factory"], FTPSERVER["Station"])

# GHI DỮ LIỆU VÀO DATABASE
        write_data_to_database(Sensor_1, Sensor_2, Sensor_3, Sensor_4, Sensor_5, Sensor_6,
                       Sensor_7, Sensor_8, Sensor_9)

# CONNECT VÀO FTP SERVER
        connect(FTPSERVER["Host"], FTPSERVER["Username"], FTPSERVER["Password"])

# TẠO FOLDER TRÊN SERVER
        createFolderFTP('data')
        connect(FTPSERVER["Host"], FTPSERVER["Username"], FTPSERVER["Password"])

# UPLOAD FILE TEXT LÊN SERVER
        uploadFileFTP(real_path)


