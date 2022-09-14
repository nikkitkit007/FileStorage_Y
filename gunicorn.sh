#!/bin/sh
gunicorn --chdir cloud_file_storage_controller/api server:app -w 2 --threads 2 -b 0.0.0.0:80
