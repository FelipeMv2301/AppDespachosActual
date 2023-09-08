# App Despachos

## Requisitos

Asegúrate de tener instalado lo siguiente en tu máquina antes de continuar:

- Python v3.10: [Instrucciones de instalación](https://www.python.org/downloads/)
- MySQL: [Instrucciones de instalación](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/)

## Instalación

1. Clona el repositorio en tu máquina:
    ```sh
    git clone https://github.com/bioquimica-cl/despachos.git
    ```
2. Entra al directorio del proyecto:
    ```sh
    cd despachos
    ```
3. Ejecuta la configuración de Linux:
    ```sh
    source ./util/linux_setup.sh <enviroment['dev','prod']>
    ```
4. Configura el uso y acceso de MySQL local:

    ```sh
    sudo mysql -u root
    > CREATE SCHEMA '<mysqlschema>' ;
    > CREATE USER '<mysqluser>'@'<mysqlhost>' IDENTIFIED BY '<mysqlpassword>';
    > GRANT ALL PRIVILEGES ON *.* TO'<mysqluser>'@'<mysqlhost>'
    > FLUSH PRIVILEGES;
    ```
5. Edita en el archivo .env del proyecto la información de MySQL:
    ```env
    # Database for Django
    # ------------------------------------------
    DB_ENGINE=django.db.backends.mysql
    DB_HOST=<mysqlhost>
    DB_PORT=<mysqlport>
    DB_NAME=<mysqlschema>
    DB_USER=<mysqluser>
    DB_PASSWORD=<mysqlpassword>
    ```
6. Ejecuta la configuración del proyecto:
    ```sh
    source ./util/app_setup.sh
    ```

Con estos pasos completados satisfactoriamente, el proyecto se encontrará apto para ser manipulado y no será necesario ejecutarlos de nuevo.

## Comandos más utilizados

Los comandos más utilizados en el proyecto tienen un alias de consola en el archivo ./util/.bash_aliases

### Python

1.
    ```sh
    python3 -m <module>
    ```
    Ejecuta el módulo de biblioteca como un script.

### Entorno virtual de Python

1.
    ```sh
    source ./venv/bin/activate
    ```
    Activa el entorno virual de Python creado previamente.
    [Documentación aquí](https://docs.python.org/3/library/venv.html#how-venvs-work)
    
2.
    ```sh
    deactivate
    ```
    Desactiva el entorno virual de Python activado previamente.

### Django

1.
    ```sh
    python3 manage.py collectstatic
    ```
    Recopila archivos estáticos de cada una de sus aplicaciones en una única ubicación que se puede servir fácilmente en producción.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/#collectstatic)

2.
    ```sh
    python3 manage.py startapp <appname> <directory>
    ```
    Crea una estructura de directorio de aplicaciones de Django para el nombre de la aplicación dada en el directorio actual o el destino dado.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#startapp)

3.
    ```sh
    python3 manage.py makemigrations <app_label1> <app_label2>
    ```
    Crea nuevas migraciones en función de los cambios detectados en sus modelos.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#makemigrations)

4.
    ```sh
    python3 manage.py migrate <app_label> <migration_name>
    ```
    Sincroniza el estado de la base de datos con el conjunto actual de modelos y migraciones.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#migrate)

5.
    ```sh
    python3 manage.py runserver
    ```
    Inicia un servidor web de desarrollo ligero en la máquina local. De forma predeterminada, el servidor se ejecuta en el puerto 8000 en la dirección IP 127.0.0.1. Puede pasar una dirección IP y un número de puerto de forma explícita.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#runserver)

6.
    ```sh
    python3 manage.py shell
    ```
    Inicia el intérprete interactivo de Python para Django.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#shell)

7.
    ```sh
    python3 manage.py shell < <path/to/file/pythonfilename.py>
    ```
    Ejecuta archivo del proyecto con el intérprete interactivo de Python para Django.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#shell)

8.
    ```sh
    python3 manage.py shell_plus
    ```
    Shell de Django con carga automática de los modelos de base de datos de aplicaciones y subclases de clases definidas por el usuario.
    [Documentación aquí](https://django-extensions.readthedocs.io/en/latest/shell_plus.html)

9.
    ```sh
    python3 manage.py createsuperuser
    ```
    Crea una cuenta de superusuario (un usuario que tiene todos los permisos).
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#createsuperuser)

10.
    ```sh
    python3 manage.py dumpdata <app_label.ModelName> <path/to/file/outputfilename>
    ```
    Obtiene a la salida estándar todos los datos en la base de datos asociados con las aplicaciones nombradas.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#dumpdata)

11.
    ```sh
    python3 manage.py loaddata <path/to/file/filename>
    ```
    Busca y carga el contenido de la colección de datos nombrada en la base de datos.
    [Documentación aquí](https://docs.djangoproject.com/en/4.2/ref/django-admin/#loaddata)
