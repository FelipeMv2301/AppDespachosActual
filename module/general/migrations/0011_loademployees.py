import os
from pathlib import Path

from django.core.management import call_command
from django.db import migrations

CURRENT_PATH = Path(__file__).parent.resolve()


def forwards_func(apps, schema_editor):
    CURRENT_PATH = Path(__file__).parent.resolve()
    data_path = os.path.join(CURRENT_PATH, 'data')
    data_file_names = [
        'employee5.json',
        'employee_service4.json',
    ]
    for filename in data_file_names:
        call_command('loaddata', os.path.join(data_path, filename))


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0010_loadservice'),
    ]

    operations = [
        migrations.RunPython(code=forwards_func, reverse_code=reverse_func),
    ]
