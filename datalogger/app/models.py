from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_per',
        related_query_name='user',
    )

class Login(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

class YourModel(models.Model):
    field1 = models.CharField(max_length=100)
    field2 = models.IntegerField()

from django.utils import timezone

class Sensor1(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    def __str__(self):
        return self.name

class Sensor2(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.name

class Sensor3(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    def __str__(self):
        return self.name

class Sensor4(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.name

class Sensor5(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    def __str__(self):
        return self.name

class Sensor6(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.name

class Sensor7(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    def __str__(self):
        return self.name

class Sensor8(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.name
class Sensor9(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=100, default='default unit')
    timestamp = models.DateTimeField()  # Không sử dụng auto_now_add
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.name
class Alarm(models.Model):
    value = models.FloatField(default=0.0)  # Đảm bảo giá trị mặc định hợp lệ
    timestamp = models.DateTimeField(auto_now_add=True)

class DeviceConfig(models.Model):
    name = models.CharField(max_length=100, default='default name')
    volmax = models.FloatField(default=0.0)  # Đảm bảo giá trị mặc định hợp lệ
    volmin = models.FloatField(default=0.0)  # Đảm bảo giá trị mặc định hợp lệ
    input = models.CharField(max_length=100, default='default input')
    def __str__(self):
        return self.name
class Settings(models.Model):
    sensor_name = models.CharField(max_length=255,default='default name')
    unit = models.CharField(max_length=50,default='default unit')
    min_value = models.FloatField(default=0.0)
    max_value = models.FloatField(default=0.0)
    min_alarm = models.FloatField(default=0.0)
    max_alarm = models.FloatField(default=0.0)
    def __str__(self):
        return self.sensor_name
class RS485Settings(models.Model):
    name = models.CharField(max_length=100)
    baudrate = models.IntegerField()
    port = models.CharField(max_length=50)
    sensor_id = models.IntegerField()
    address = models.IntegerField()
    sensor_type = models.CharField(max_length=50)
    min_alarm = models.FloatField()
    max_alarm = models.FloatField()

class DigitalSettings(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    gpio = models.IntegerField()
    min_alarm = models.FloatField()
    max_alarm = models.FloatField()
    status = models.CharField(max_length=50)

class Schedule(models.Model):
    port = models.CharField(max_length=10)
    param1 = models.FloatField()
    param2 = models.FloatField()

    def __str__(self):
        return f'Schedule for {self.port}'
class Error(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    type= models.CharField(max_length=100)
    location = models.CharField(max_length=100) 
    describe= models.CharField(max_length=100)
    
