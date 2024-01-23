
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point
from confluent_kafka import Consumer, KafkaError
import time, os, threading, subprocess

# Print the parsed configuration
print("InfluxDB Configuration:")
print("Bucket:", os.environ.get('INFLUXDB_BUCKET'))
print("Organization:", os.environ.get('INFLUXDB_ORG'))
print("Token:", os.environ.get('INFLUXDB_TOKEN'))

print("\nKafka Configuration:")
print("Bootstrap Servers:", os.environ.get('KAFKA_BOOTSTRAP_SERVERS'))
print("Topic:", os.environ.get('KAFKA_TOPIC'))

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
        'auto.offset.reset': 'earliest'  # Start consuming from the beginning of the topic
    }

    # Create a Kafka consumer instance
    consumer = Consumer(conf)

    # Subscribe to the topic
    consumer.subscribe([topic])

    dem = 0
    points = []
    try:
        print(f'Consuming in group {groupId}...')
        while not stop_flag.is_set():
            msg = consumer.poll(1.0)  # Poll for messages with a timeout (in seconds)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('Reached end of partition')
                else:
                    print('Error: {}'.format(msg.error()))
            else:
                # print(msg.value().decode('utf-8'))
                try:
                    point = kafkaMessageToInfluxdbPoint(msg.value().decode('utf-8'))
                    if point is not None:
                        points.append(point)
                    dem += 1
                    if dem == 1000:
                        try:
                            print('push')
                            write_api.write(bucket=bucket, org=org, record=points)
                        except Exception as e:
                            print(e)
                            consumer.close()
                            print(endpoints, influxdbUrl)
                            if influxdbUrl in endpoints:
                              endpoints.remove(influxdbUrl)
                            return
                        dem = 0
                        points = []
                    
                except Exception as e:
                    print(msg.value())
                    print(e)
    except Exception as e:
        print(e)
        consumer.close()
        if influxdbUrl in endpoints:
            endpoints.remove(influxdbUrl)
    finally:
        consumer.close()

def getHeadLessServiceEndpoints():
    headlessService = os.environ.get('HEADLESS_SERVICE')
    command = f"nslookup -type=SRV {headlessService} | grep 8086 | awk '{{print $7}}' | uniq | sed 's/.$//g'"
    output = subprocess.check_output(command, shell=True, text=True)
    return output.split('\n')[:-1]

if __name__ == '__main__':
    # Termination flag
    stop_flag = threading.Event()

    threads = []

    endpoints = []

    while True:
        tmp = getHeadLessServiceEndpoints()
        if tmp != endpoints:
            endpoints = tmp[:]
            stop_flag.set()
            for thread in threads:
                thread.join()
            threads = []
            stop_flag.clear()
            for endpoint in endpoints:
                thread = threading.Thread(target=process, args=(endpoint, endpoint.split('.')[0],))
                threads.append(thread)
                thread.start()
        time.sleep(60)
