from django.contrib import admin

# Register your models here.
from .models import Sensor2
admin.site.register(Sensor2)
from .models import Sensor1
admin.site.register(Sensor1)
from .models import Sensor3
admin.site.register(Sensor3)
from .models import Sensor4
admin.site.register(Sensor4)
from .models import Sensor5
admin.site.register(Sensor5)
from .models import Sensor6
admin.site.register(Sensor6)
from .models import Sensor7
admin.site.register(Sensor7)
from .models import Sensor8
admin.site.register(Sensor8)
from .models import Sensor9
admin.site.register(Sensor9)
from .models import(Settings)
admin.site.register(Settings)
from .models import Error
admin.site.register(Error)
from .models import DeviceConfig
admin.site.register(DeviceConfig)
from .models import(RS485Settings)
admin.site.register(RS485Settings)
from .models import(DigitalSettings)
admin.site.register(DigitalSettings)