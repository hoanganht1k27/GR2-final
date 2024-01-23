import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point
from confluent_kafka import Consumer, KafkaError
import time, os, threading, subprocess, logging


# Create a logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler("log.log")
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Print the parsed configuration
logger.info("InfluxDB Configuration:")
logger.info(f"Bucket: {os.environ.get('INFLUXDB_BUCKET')}")
logger.info(f"Organization: {os.environ.get('INFLUXDB_ORG')}")
logger.info(f"Token: {os.environ.get('INFLUXDB_TOKEN')}")

logger.info(f"Kafka Configuration:")
logger.info(f"Bootstrap Servers: {os.environ.get('KAFKA_BOOTSTRAP_SERVERS')}")
logger.info(f"Topic: {os.environ.get('KAFKA_TOPIC')}")

bucket = os.environ.get('INFLUXDB_BUCKET')
org = os.environ.get('INFLUXDB_ORG')
token = os.environ.get('INFLUXDB_TOKEN')
bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS')
topic = os.environ.get('KAFKA_TOPIC')

def kafkaMessageToInfluxdbPoint(str):
    try:
        isEscaped = False
        curStr = ""
        id = 0
        measurement = ""

        # Get measurement
        for i in range(0, len(str)):
            if str[i] == ',':
                id = i + 1
                break

        measurement = str[:id - 1]
        tags = []

        # Get tags
        i = id
        while i < len(str):
            if str[i] == '\\':
                isEscaped = True
            elif str[i] == '=':
                if isEscaped:
                    curStr += str[i]
                    isEscaped = False
                else:
                    tag = curStr
                    j = i + 1
                    curStr = ""
                    while j < len(str):
                        if str[j] == '\\':
                            isEscaped = True
                        else:
                            if str[j] == ',' or str[j] == ' ':
                                if isEscaped:
                                    curStr += str[j]
                                    isEscaped = False
                                else:
                                    break
                            else:
                                curStr += str[j]
                                isEscaped = False
                        j += 1
                    tags.append([tag, curStr])
                    curStr = ""
                    i = j
                    if str[i] == ' ':
                        i += 1
                        break
            else:
                curStr += str[i]
                isEscaped = False
            i += 1

        str = str[i:].split(' ')
        fields = str[0].split('=')
        timeStamp = int(str[1].replace('\n', ''))
        p = Point(measurement)
        for t in tags:
            p = p.tag(t[0], t[1])

        p = p.field(fields[0], float(fields[1]))
        p = p.time(timeStamp)
        return p
    except:
        return None

def process(influxdbUrl, groupId):
    client = influxdb_client.InfluxDBClient(
        url=f"{influxdbUrl}:8086",
        token=token,
        org=org
    )

    # Write script
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Kafka consumer configuration
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': groupId,
        'auto.offset.reset': 'earliest',  # Start consuming from the beginning of the topic
        'enable.auto.commit': False
    }

    # Create a Kafka consumer instance
    consumer = Consumer(conf)

    # Subscribe to the topic
    consumer.subscribe([topic])

    points = []
    try:
        logger.info(f'Consuming in group {groupId}...')
        noMessageCount = 0
        while not isStop:
            messages = consumer.consume(num_messages=12000, timeout=30)
            if not messages:
                noMessageCount += 1
                if noMessageCount >= 20:
                  raise ValueError(f'No message has been consume in group {groupId} for 10 minutes, stop consuming ...')
                continue
            else:
                noMessageCount = 0
                for msg in messages:
                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            print('Reached end of partition')
                        else:
                            print('Error: {}'.format(msg.error()))
                    else:
                        try:
                            point = kafkaMessageToInfluxdbPoint(msg.value().decode('utf-8'))
                            if point is not None:
                                points.append(point)
                        except Exception as e:
                            logger.error(f'Thread {influxdbUrl} - Error when parsing message {msg.value()} from kafka to influxdb data point')
                try:
                    write_api.write(bucket=bucket, org=org, record=points)
                    consumer.commit(asynchronous=True)
                except Exception as e:
                    logger.error(f'Thread {influxdbUrl} - Error when pushing data to {influxdbUrl}')
                    logger.error(e)
                    logger.info(f'Thread {influxdbUrl} - Retry...')
                    # consumer.close()
                    # if influxdbUrl in endpoints:
                    #     endpoints.remove(influxdbUrl)
                    # points = []
                    # break
                points = []
    except Exception as e:
        logger.error(f'Some error has been occurred in thread of {influxdbUrl}')
        logger.error(e)
        consumer.close()
        if influxdbUrl in endpoints:
            endpoints.remove(influxdbUrl)
    finally:
        logger.info(f'Consumer in group {groupId} finished')
        consumer.close()

def getHeadLessServiceEndpoints():
    headlessService = os.environ.get('HEADLESS_SERVICE')
    command = f"nslookup -type=SRV {headlessService} | grep 8086 | awk '{{print $7}}' | uniq | sed 's/.$//g'"
    output = subprocess.check_output(command, shell=True, text=True)
    return output.split('\n')[:-1]

if __name__ == '__main__':
    # Termination flag
    isStop = False

    threads = []

    endpoints = getHeadLessServiceEndpoints()
    
    for endpoint in endpoints:
      thread = threading.Thread(target=process, args=(endpoint, endpoint.split('.')[0],))
      threads.append(thread)
      thread.start()

    while True:
        tmp = getHeadLessServiceEndpoints()

        if tmp != endpoints:
            isStop = True
            #for thread in threads:
            #    thread.join()
            logger.info('Consumer stopped')
            break
        time.sleep(60)
