# SMS-Simulator Project

The SMS-Simulator is a sophisticated application designed to emulate the sending and receiving of SMS messages via a message broker system. It leverages RabbitMQ for message queuing, Redis for caching, and Logstash for logging, Elastic Search for storing logs, and Kibana for visualizing the progress of message-sent, failed and processing time.

![Architecture Diagram](./screenshots/Architecture.png)

## Configuration

Major parameters are configured inside the .env file, for some parameters you need to configure it in the docker-compose file and in the kibana dashboard.

### Producer

To adjust the number of messages produced, modify the `TOTAL_MESSAGES` field in the producer section of the environment file.

- **TOTAL_MESSAGES**: `10000`
  - This parameter sets the total number of messages to be produced.
- **PRODUCER_RUN_FOREVER**: `False`
  - This parameter determines whether the producer should run indefinitely.
- **PRODUCER_MSG_DELAY**: `0.5`
  - This parameter sets the delay (in seconds) between producing each message.

### Sender

ou can adjust the number of senders by modifying the `replicas` field in the Docker Compose file under the sender service.

![Screenshot of the sender service inside the docker-compose file ](./screenshots/Screenshot.png)

To configure the mean processing time and failure rate for each sender, update the `MESSAGE_PROCESSING_TIME` and `FAILURE_RATE` parameters in the environment file. Length of `MESSAGE_PROCESSING_TIME` and `FAILURE_RATE` equals number of senders

- **MESSAGE_PROCESSING_TIME**: `[[0.5, 0.1], [0.4, 0.1]]`
  - The first parameter is the mean processing time in seconds, and the second parameter is the standard deviation used for generating random values from gaussian distribution.
- **FAILURE_RATE**: `[[0.9], [0.9]]`
  - This parameter sets the failure rate for each sender which will be used to generate failure count from bernoulli distribution.

### Progress Monitor

To change the refresh rate in a Kibana dashboard, follow these steps:

1. **Open the Dashboard**: Navigate to the dashboard you want to modify in Kibana.

2. **Click on "Refresh" Button**: In the top-right corner of the dashboard, you'll see a "Refresh" button. Click on it.

3. **Select a Refresh Interval**: A dropdown menu will appear with various options for refresh intervals. You can choose from options like 5 seconds, 10 seconds, 30 seconds, 1 minute, etc. Additionally, you can select "Off" if you don't want the dashboard to automatically refresh.

4. **Save the Dashboard**: Once you've selected the desired refresh interval, you can save the dashboard if you want to retain this setting for future use.

![Refresh rate](./screenshots/kibana.png)
