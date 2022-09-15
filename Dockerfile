FROM python:latest

WORKDIR /usr/src/app
COPY . ./
RUN pip3 install -r requirements.txt
RUN chmod +x ./gunicorn.sh

#CMD ["python", "/usr/src/app/cloud_file_storage_controller/api/server.py"]
ENTRYPOINT ["./gunicorn.sh"]
