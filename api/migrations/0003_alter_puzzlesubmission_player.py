# Generated by Django 4.2.17 on 2024-12-24 09:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_puzzle_time_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzlesubmission',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
