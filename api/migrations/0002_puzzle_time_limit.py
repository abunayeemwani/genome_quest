# Generated by Django 4.2.17 on 2024-12-24 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='time_limit',
            field=models.IntegerField(default=120, help_text='Time limit in seconds to complete the puzzle'),
        ),
    ]
