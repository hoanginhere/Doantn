# Generated by Django 3.2 on 2023-11-11 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_sensor1_sensor2'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter1', models.FloatField()),
                ('parameter2', models.FloatField()),
            ],
        ),
    ]
