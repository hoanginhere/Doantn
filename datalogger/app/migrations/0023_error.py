# Generated by Django 3.2 on 2024-06-23 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20240620_1131'),
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('describe', models.CharField(max_length=100)),
            ],
        ),
    ]
