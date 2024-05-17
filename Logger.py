import logging
import logstash
import os
from dotenv import load_dotenv
load_dotenv()

def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    logstash_host, logstash_port = os.getenv('LOGSTASH_HOST'), os.getenv('LOGSTASH_PORT')
    logger.addHandler(logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1))
    logging.getLogger().setLevel(logging.ERROR)
    return logger

