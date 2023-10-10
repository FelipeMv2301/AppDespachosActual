#!/bin/bash

ENVIRONMENT=$1

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

# Update and install basic packages
sudo apt update -y
sudo apt upgrade -y

# Install required packages
sudo apt install -y boxes python3 python3-pip python3-dev build-essential libssl-dev libffi-dev
sudo apt-get install -y python3-virtualenv python3.10-venv

# Install and configure MySQL
sudo apt install -y libmysqlclient-dev mysql-client

if [ "$ENVIRONMENT" = "prod" ]; then
    # Install Apache and configure mod_wsgi
    sudo apt install -y apache2 libapache2-mod-wsgi-py3
    sudo a2enmod wsgi ssl
    sudo ufw app list
    sudo ufw allow 'Apache'

    # Get Apache path
    APACHE_DIR=$(apache2ctl -V | grep -oP '(?<=HTTPD_ROOT=").*(?=")')

    # Edit Apache vars
    APACHE_VARS_FILE="${APACHE_DIR}/envvars"
    NEW_APACHE_RUN_USER="$USER"
    sudo sed -i "s/export APACHE_RUN_USER=.*/export APACHE_RUN_USER=${NEW_APACHE_RUN_USER}/" "${APACHE_VARS_FILE}"
    sudo sed -i "s/export APACHE_RUN_GROUP=.*/export APACHE_RUN_GROUP=${NEW_APACHE_RUN_USER}/" "${APACHE_VARS_FILE}"

    # Configure timezone
    sudo timedatectl set-timezone "America/Santiago"
fi

# Print finished message
echo "FINISHED" | boxes
