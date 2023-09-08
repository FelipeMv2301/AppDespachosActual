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
python3 "${MANAGE_PATH}" shell -c "from django.contrib.auth.models import User; User.objects.create_superuser(username='django', email='app@bioquimica.cl', password='iShiNDrog3YmO')"

# Run the rest of migrations
python3 "${MANAGE_PATH}" migrate

# Print finished message
echo "FINISHED" | boxes
