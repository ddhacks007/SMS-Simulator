FROM python:3.12
COPY Producer/requirements.txt .
RUN pip install -r requirements.txt
COPY Producer/* .
COPY RabbitMQClient.py .
COPY Logger.py .
CMD ["python3", "Main.py"]