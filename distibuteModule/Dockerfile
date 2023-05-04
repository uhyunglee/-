FROM python:3.9
RUN apt-get update && apt-get install -y libgl1-mesa-glx
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
EXPOSE 5001
RUN pip install --trusted-host pypi.python.org -r requirements.txt
CMD ["python", "distributed_flask.py"]