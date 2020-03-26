import connexion
from connexion import NoContent
import requests
import json
from pykafka import KafkaClient
from datetime import datetime
import yaml


try:
    with open('/config/app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())

except FileNotFoundError:
    with open('app_conf.yaml', 'r') as f:
        app_config = yaml.safe_load(f.read())

def get_request_history(requestNum):
    client = KafkaClient(hosts="{}:{}".format(app_config['kafka']['server'], app_config['kafka']['port']))
    topic = client.topics['events']
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)

    reqlist = []
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg['type'] == 'request':
            reqlist.append(msg)

    if requestNum >= len(reqlist):
        return NoContent, 404
    return reqlist[requestNum], 200


def get_report_oldest():
    client = KafkaClient(hosts="{}:{}".format(app_config['kafka']['server'], app_config['kafka']['port']))
    topic = client.topics['events']
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=100)

    replist = []
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg['type'] == 'report':
            replist.append(msg)

    if len(replist) == 0 :
        return NoContent, 404
    else:
        return replist[-1], 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml")

if __name__ == "__main__":
    app.run(port=8040)

