#!/bin/bash
echo "Updating server"
git pull
echo "Instaling all from requirements"
python3 -m pip install -r requirements.txt
echo "Aplying migrations"
python3 manage.py migrate
echo "Starting server"
python3 manage.py runserver 0.0.0.0:8000
