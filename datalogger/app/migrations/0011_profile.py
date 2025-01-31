# Generated by Django 3.2 on 2024-05-07 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_device_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=80)),
                ('bio', models.TextField(blank=True, max_length=254)),
                ('profile_picture', models.ImageField(upload_to='photos/')),
            ],
        ),
    ]
