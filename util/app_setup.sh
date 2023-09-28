#!/bin/bash

if [ "$USER" != "ubuntu" ]; then
    echo "WARNING: The running user is not 'ubuntu'."
    read -p "You want to continue anyway? (y/n) " choice
    case "$choice" in
        y|Y )
            echo "Continuing with the execution..."
            ;;
        * )
            echo "Aborting execution."
            return
            ;;
    esac
fi

# Defines the paths
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BASE_DIR=$(dirname "$SCRIPT_DIR")
MANAGE_PATH="${BASE_DIR}/manage.py"

# Activate the virtual environment
source "${BASE_DIR}/venv/bin/activate"

# Install Python dependencies
python3 -m pip install -r "${BASE_DIR}/requirements.txt"

# Run the initial migrations
native_apps=$(python3 "${MANAGE_PATH}" shell -c "from django.apps import apps; django_apps = [app.label for app in apps.get_app_configs() if app.name.startswith('django.contrib')]; print(','.join(django_apps))")
IFS=',' read -ra elements <<< "$native_apps"
for element in "${elements[@]}"
do
    python3 "${MANAGE_PATH}" migrate "${element}"
done

# Create a super user
python3 "${MANAGE_PATH}" shell -c "
from django.contrib.auth.models import User
User.objects.create_superuser(username='django', email='app@bioquimica.cl', password='iShiNDrog3YmO')
"

# Run the rest of migrations
python3 "${MANAGE_PATH}" migrate

# Create customized user permissions
python3 "${MANAGE_PATH}" shell -c "
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from app.delivery.models.delivery import Delivery

content_type = ContentType.objects.get_for_model(model=Delivery)


objs = [
    Permission(
        codename='view_kpis',
        name='Can view KPIs',
        content_type=content_type
    ),
    Permission(
        codename='edit_delivery',
        name='Can edit delivery',
        content_type=content_type
    ),
    Permission(
        codename='edit_delivery_form',
        name='Can edit all delivery form fields',
        content_type=content_type
    ),
    Permission(
        codename='edit_delivery_form_rcpt_commit_date',
        name='Can edit the commitment date field on delivery form',
        content_type=content_type
    ),
    Permission(
        codename='edit_delivery_rcpt_commit_date',
        name='Can edit delivery reception commitment date',
        content_type=content_type
    ),
    Permission(
        codename='issue_delivery',
        name='Can issue delivery',
        content_type=content_type
    ),
    Permission(
        codename='cancel_delivery',
        name='Can cancel delivery',
        content_type=content_type
    ),
    Permission(
        codename='view_delivery_panel',
        name='Can view delivery panel',
        content_type=content_type
    ),
]

Permission.objects.bulk_create(objs=objs)
"

python3 "${MANAGE_PATH}" shell < "${BASE_DIR}/jobs/stk_agency_sync.py"
python3 "${MANAGE_PATH}" shell < "${BASE_DIR}/jobs/deliv_opt_sync.py"

# # Print finished message
# echo "FINISHED" | boxes
