from django.contrib import admin
from django.urls import path
from app.views import error, error_results,weather_view
from app.views import csv_list,show_alarms,view_csv, graph, schedule_view, index, ftp_form, device_config,mqtt_alarm,fetch_sensor_data, upload_firmware,device_config_success
from app.views import get_sensor_data, alarm_view,show_alarms, login_view , logout_view, register, home , settings_view,  query_results, query
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register,name='register' ),
    path('home/', home, name='home'),
    path('settings/', settings_view, name='settings'),
    path('values/', index, name='values'),
    path('query_results/', query_results, name='query_results'),
    path('query/', query, name='query'),
    path('csv_list/', csv_list, name='csv_list'),
    path('error/', error, name='error'),
    path('error_results/', error_results, name='error_results'),
    path('weather/', weather_view, name='weather'),
    path('ftp_setting/', ftp_form, name='ftp_form'),
    path('schedule/', schedule_view, name='schedule'),
    path('get_sensor_data/', get_sensor_data, name='get_sensor_data'),
    path('device/', device_config, name='device'),
    path('mqtt_alarm/', mqtt_alarm, name='mqtt_alarm'),
    path('graph/', graph, name='graph'),
    path('fetch_sensor_data/', fetch_sensor_data, name='fetch_sensor_data'),
    path('upload_firmware/', upload_firmware, name='upload_firmware'),
    path('device_config_success/', device_config_success, name='device_config_success'),
    path('view_csv/<str:file_name>/',view_csv, name='view_csv'),





]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()