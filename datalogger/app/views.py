from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
import os
from django.template.loader import render_to_string
import csv
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render
from django.conf import settings

from .models import DeviceConfig, Sensor1, Sensor2, Sensor3, Sensor4, Sensor5, Sensor6,Sensor7,Sensor8, Settings,Sensor9
import json
import paho.mqtt.client as mqtt
from django.shortcuts import render
from django.shortcuts import render
from .models import Alarm
import paho.mqtt.client as mqtt
from django.http import JsonResponse
import time
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def mqtt_alarm(request):
    if request.method == 'POST':
        # Xử lý tin nhắn từ MQTT ở đây
        # Để đơn giản, chúng ta sẽ chỉ trả về dữ liệu JSON cho client
        data = {'message': 'Received MQTT alarm message'}
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request method'})

# Hàm đăng kí người dùng
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
#Hàm đăng nhập người dùng
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'login.html')
#Hàm đăng xuất
def logout_view(request):
    logout(request)
    return redirect('login')
def home(request):
    return render(request,'home.html' )
# Hàm trả về kết quả truy vấn

def query_results(request):
    table = request.GET.get('table')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    # Truy vấn dữ liệu quá khứ tương ứng với bảng được chọn
    if table == 'Sensor1':
        queried_data = Sensor1.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor2':
        queried_data = Sensor2.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor3':
        queried_data = Sensor3.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor4':
        queried_data = Sensor4.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor5':
        queried_data = Sensor5.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor6':
        queried_data = Sensor6.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor7':
        queried_data = Sensor7.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor8':
        queried_data = Sensor8.objects.filter(timestamp__range=[start_time, end_time])
    elif table == 'Sensor9':
        queried_data = Sensor9.objects.filter(timestamp__range=[start_time, end_time])
    else:
        queried_data = []

    return render(request, 'query_results.html', {'data': queried_data, 'table': table})
def query(request):
    return render(request,'query.html' )

#Hàm hiển thị dữ liệu thời gian thực
import json
import time
from django.http import JsonResponse
import paho.mqtt.client as mqtt
import logging

def get_sensor_data(request, timeout=5):
    # Thông tin kết nối MQTT
    broker = 'broker.emqx.io'
    port = 1883
    sensor_data = {f'sensor{i}': None for i in range(1, 10)}

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Đã kết nối tới MQTT broker với mã kết quả {rc}")
            for i in range(1, 10):
                client.subscribe(f'sensor/{i}')
        else:
            print(f"Không thể kết nối tới MQTT broker với mã kết quả {rc}")

    def on_message(client, userdata, msg):
        topic_index = msg.topic.split('/')[-1]
        sensor_data[f'sensor{topic_index}'] = json.loads(msg.payload.decode("utf-8"))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(broker, port, 60)
        client.loop_start()

        start_time = time.time()
        while time.time() - start_time < timeout:
            if all(value is not None for value in sensor_data.values()):
                break
            time.sleep(0.1)
        while time.time() - start_time < 10:
            time.sleep(0.1)
        client.loop_stop()
        client.disconnect()

        # Default values for sensors without data
        for key, value in sensor_data.items():
            if value is None:
                sensor_data[key] = {'timestamp': None, 'name': None, 'value': None, 'unit': None}

        data = {key: {
                    'timestamp': value['timestamp'],
                    'name': value['name'],
                    'value': value['value'],
                    'unit': value['unit']
                } for key, value in sensor_data.items()}
        

        return JsonResponse(data)
    except Exception as e:
        logging.error("Error in get_sensor_data: %s", e)
        return JsonResponse({'error': 'An error occurred while fetching sensor data.'}, status=500)
from django.shortcuts import render

def index(request):
    return render(request, 'value.html')

# Khởi tạo một client MQTT


# MQTT configuration
client = mqtt.Client()


import json
import paho.mqtt.client as mqtt
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Settings, RS485Settings, DigitalSettings

def settings_view(request):
    client = mqtt.Client()
    client.connect("broker.emqx.io", 1883, 60)

    if request.method == 'POST':
        sensor_type = request.POST.get('sensor_type')

        if sensor_type == 'regular':
            # Xử lý cài đặt cảm biến thường
            port = request.POST.get('port')
            sensor_name = request.POST.get('sensor_name')
            sensor_unit = request.POST.get('sensor_unit')
            sensor_min_value = float(request.POST.get('sensor_min_value'))
            sensor_max_value = float(request.POST.get('sensor_max_value'))
            sensor_min_alarm = float(request.POST.get('sensor_min_alarm'))
            sensor_max_alarm = float(request.POST.get('sensor_max_alarm'))

            # Save sensor data to the database
            sensor_data = Settings(
                sensor_name=sensor_name,
                unit=sensor_unit,
                min_value=sensor_min_value,
                max_value=sensor_max_value,
                min_alarm=sensor_min_alarm,
                max_alarm=sensor_max_alarm
            )
            sensor_data.save()
            config = "config/port" + port

            # Prepare MQTT data
            sensor_data_mqtt = {
                "Name": sensor_name,
                "Unit": sensor_unit,
                "Min_Value": sensor_min_value,
                "Max_Value": sensor_max_value,
                "Min_Alarm": sensor_min_alarm,
                "Max_Alarm": sensor_max_alarm,
                "Status": 1  # Adjust status as needed
            }
            client.publish(config, json.dumps(sensor_data_mqtt))

        elif sensor_type == 'rs485':
            # Xử lý cài đặt cảm biến RS485
            rs485_name = request.POST.get('rs485_name')
            rs485_baudrate = int(request.POST.get('rs485_baudrate'))
            rs485_port = request.POST.get('rs485_port')
            rs485_id = int(request.POST.get('rs485_id'))
            rs485_address = int(request.POST.get('rs485_address'))
            rs485_type = request.POST.get('rs485_type')
            rs485_min_alarm = float(request.POST.get('rs485_min_alarm'))
            rs485_max_alarm = float(request.POST.get('rs485_max_alarm'))

            # Save RS485 sensor data to the database
            rs485_data = RS485Settings(
                name=rs485_name,
                baudrate=rs485_baudrate,
                port=rs485_port,
                sensor_id=rs485_id,
                address=rs485_address,
                sensor_type=rs485_type,
                min_alarm=rs485_min_alarm,
                max_alarm=rs485_max_alarm
            )
            rs485_data.save()

            # Prepare MQTT data for RS485
            rs485_data_mqtt = {
                "Name": rs485_name,
                "Baudrate": rs485_baudrate,
                "Port": rs485_port,
                "ID": rs485_id,
                "Address": rs485_address,
                "Type": rs485_type,
                "Min_Alarm": rs485_min_alarm,
                "Max_Alarm": rs485_max_alarm
            }
            client.publish("config/rs485", json.dumps(rs485_data_mqtt))

        elif sensor_type == 'digital':
            # Xử lý cài đặt cảm biến Digital
            digital_name = request.POST.get('digital_name')
            digital_unit = request.POST.get('digital_unit')
            digital_gpio = int(request.POST.get('digital_gpio'))
            digital_min_alarm = float(request.POST.get('digital_min_alarm'))
            digital_max_alarm = float(request.POST.get('digital_max_alarm'))
            digital_status = request.POST.get('digital_status')

            # Save digital sensor data to the database
            digital_data = DigitalSettings(
                name=digital_name,
                unit=digital_unit,
                gpio=digital_gpio,
                min_alarm=digital_min_alarm,
                max_alarm=digital_max_alarm,
                status=digital_status
            )
            digital_data.save()
            print("đã lưu")

            # Prepare MQTT data for Digital
            digital_data_mqtt = {
                "Name": digital_name,
                "Unit": digital_unit,
                "GPIO": digital_gpio,
                "Min_Alarm": digital_min_alarm,
                "Max_Alarm": digital_max_alarm,
                "Status": digital_status
            }
            client.publish("config/digital", json.dumps(digital_data_mqtt))

        messages.success(request, 'Cài đặt thành công!')
        return redirect('home')

    return render(request, 'settings.html')
def show_alarms(request):
    alarms = Alarm.objects.all()  # Lấy tất cả các đối tượng cảnh báo từ cơ sở dữ liệu
    context = {
        'alarms': alarms
    }
    return render(request, 'show_alarms.html', context)


def alarm_view(request):
    sensor1_values = Sensor1.objects.latest()
    sensor2_values = Sensor2.objects.latest()
    return render(request, 'alarm.html',{'sensor1_values': sensor1_values, 'sensor2_values': sensor2_values})

import csv
from django.shortcuts import render
from django.http import HttpResponse

def csv_list(request):
    csv_directory = 'E:\\Doantn\\Firmware\\data_output'
    csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]

    context = {'csv_files': csv_files}
    return render(request, 'csv_list.html', context)


import os
from django.shortcuts import render, HttpResponse
import csv

def view_csv(request, file_name):
    csv_directory = 'E:\\Doantn\\Firmware\\data_output'
    file_path = os.path.join(csv_directory, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            csv_data = list(csv_reader)
        
        # Truyền dữ liệu CSV và tên tệp vào template
        context = {
            'file_name': file_name,
            'csv_data': csv_data,
        }
        
        return render(request, 'view_csv.html', context)
    else:
        return HttpResponse("File not found", status=404)
#Gửi cấu hình FTP
from django.shortcuts import render
import paho.mqtt.publish as publish

import paho.mqtt.publish as publish

def ftp_form(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        factory = request.POST.get('factory')
        station = request.POST.get('station')
        ftp_host = request.POST.get('ftp_host')
        ftp_username = request.POST.get('ftp_username')
        ftp_password = request.POST.get('ftp_password')

        # Gửi thông tin FTP và các thông tin khác qua MQTT đến firmware
        mqtt_message = f"City:{city},Factory:{factory},Station:{station},Host:{ftp_host},Username:{ftp_username},Password:{ftp_password}"
        publish.single("ftp/config", mqtt_message, hostname="broker.emqx.io")

        return render(request, 'confirmation.html')

    return render(request, 'ftp_form.html')

#Gửi thời gian chạy cho từng model

import paho.mqtt.client as mqtt
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Schedule

def schedule_view(request):
    # Khởi tạo MQTT client
    client = mqtt.Client()
    client.connect("broker.emqx.io", 1883, 60)

    if request.method == 'POST':
        port = request.POST.get('port')
        param1 = float(request.POST.get('param1'))
        param2 = float(request.POST.get('param2'))

        # Lưu dữ liệu vào cơ sở dữ liệu
        schedule_data = Schedule(port=port, param1=param1, param2=param2)
        schedule_data.save()

        # Gửi dữ liệu qua MQTT
        sensor_data_mqtt = {
            'param1': param1,
            'param2': param2,
        }
        topic = f'timer{port}'
        client.publish(topic, json.dumps(sensor_data_mqtt))

        messages.success(request, 'Cài đặt thành công!')
        return redirect('home')

    return render(request, 'schedule.html')

from .models import DeviceConfig

def device_config(request):
    if request.method == 'POST':
        name = request.POST['name']
        volmax = float(request.POST['volmax'])
        volmin = float(request.POST['volmin'])
        input = request.POST['input']

        config = DeviceConfig(
            name=name,
            volmax=volmax,
            volmin=volmin,
            input=input
        )
        config.save()

        return redirect('device_config_success')
    print("đã lưu")

    return render(request, 'device.html', {})

def device_config_success(request):
    return render(request, 'device_config_success.html', {})
from datetime import  timedelta
from django.utils import timezone
def graph(request):
    return render(request, 'graph.html')

def fetch_sensor_data(request):
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)
    
    sensor_data = {}
    for i in range(1, 10):
        sensor_data[f'sensor{i}'] = globals()[f'Sensor{i}'].objects.filter(timestamp__gte=one_day_ago).order_by('-timestamp')[:50]
    
    response_data = {}
    for key, data in sensor_data.items():
        if data:
            response_data[f'{key}_name'] = data[0].name  # Lấy giá trị name mới nhất
        response_data[f'{key}_labels'] = [item.timestamp.strftime('%H:%M:%S') for item in data]
        response_data[f'{key}_values'] = [item.value for item in data]
      

    return JsonResponse(response_data)
# views.py
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
import shutil

def update_firmware(firmware_path):
    # Đường dẫn đến firmware hiện tại
    current_firmware_path = "E:/Doantn/Firmware/rs485.py"

    # Xóa firmware c ũ
    if os.path.exists(current_firmware_path):
        os.remove(current_firmware_path)

    # Di chuyển firmware mới đến vị trí cũ
    shutil.move(firmware_path, current_firmware_path)

def upload_firmware(request):
    if request.method == 'POST' and request.FILES['firmware']:
        firmware_file = request.FILES['firmware']
        fs = FileSystemStorage()
        filename = fs.save(firmware_file.name, firmware_file)
        uploaded_file_path = fs.path(filename)
        # Gọi hàm để cập nhật firmware
        update_firmware(uploaded_file_path)
        return render(request, 'upload_success.html', {'uploaded_file_path': uploaded_file_path})
    return render(request, 'upload_firmware.html')
def error(request):
    return render(request,'error.html' )
from app.models import Error
def error_results(request):
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    queried_data = Error.objects.filter(timestamp__range=[start_time, end_time])
  
    return render(request, 'error_results.html', {'data': queried_data})
import pyowm

def weather_view(request):
    # Lấy tên thành phố từ request hoặc sử dụng vị trí người dùng
    city = 'Hanoi'

    # Khởi tạo client để gọi API
    owm = pyowm.OWM('YOUR_API_KEY')

    # Lấy dữ liệu thời tiết
    observation = owm.weather_at_place(city)
    weather = observation.get_weather()

    # Lấy các thông tin cần thiết
    temperature = weather.get_temperature('celsius')['temp']
    description = weather.get_detailed_status()
    humidity = weather.get_humidity()
    wind_speed = weather.get_wind()['speed']

    # Trả về dữ liệu cho template
    context = {
        'temperature': temperature,
        'description': description,
        'humidity': humidity,
        'wind_speed': wind_speed
    }
    return render(request, 'weather.html', context)