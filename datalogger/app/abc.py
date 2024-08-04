from models import Sensor1
first_entry = Sensor1.objects.first()

if first_entry:
    print(first_entry.name, first_entry.temperature, first_entry.humidity, first_entry.timestamp)