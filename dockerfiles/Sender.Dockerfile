FROM python:3.12
COPY Sender/requirements.txt .
RUN pip install -r requirements.txt
COPY Sender/* .
COPY RedisClient.py .
COPY RabbitMQClient.py .
COPY Logger.py .
CMD ["python3", "Main.py"]