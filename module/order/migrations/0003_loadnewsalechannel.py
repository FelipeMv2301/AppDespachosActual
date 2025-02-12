import os
from pathlib import Path

from django.core.management import call_command
from django.db import migrations

CURRENT_PATH = Path(__file__).parent.resolve()


def forwards_func(apps, schema_editor):
    CURRENT_PATH = Path(__file__).parent.resolve()
    data_path = os.path.join(CURRENT_PATH, 'data')
    data_file_names = [
        'sale_channel2.json',
        'sale_channel_service2.json',
    ]
    for filename in data_file_names:
        call_command('loaddata', os.path.join(data_path, filename))


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_alter_order_options'),
    ]

    operations = [
        migrations.RunPython(code=forwards_func, reverse_code=reverse_func),
    ]