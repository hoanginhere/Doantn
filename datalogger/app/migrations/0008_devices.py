# Generated by Django 3.2 on 2024-04-26 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_outlier'),
    ]

    operations = [
        migrations.CreateModel(
            name='Devices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('IDdevice', models.CharField(max_length=100)),
            ],
        ),
    ]
