import json
import boto3
from confluent_kafka import Producer
import urllib
import logging
import certifi

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

print('Loading function')

s3 = boto3.client('s3')

producer = Producer({
    'bootstrap.servers': 'FIXME',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'FIXME',
    'sasl.password': 'FIXME',
    'ssl.ca.location': certifi.where(),
    'message.timeout.ms': 10*1000})


def delivery_report(err, msg, event):
    """ Delivery report callback is called once per message
        to indicate delivery success (err is None) or permanent
        delivery failure (err is not None).
        The callback is triggered by calling flush() or poll(). """
    if err is not None:
        print('Failed to produce event {}: {}'.format(event, err))
        #raise err
    else:
        print('Produced event {} to {} [{}]'.format(event, msg.topic(), msg.partition()))

def lambda_handler(event, context):
    """ AWS Lambda handler entry point """
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    print("We have new object. In bucket {}, with key {}".format(bucket, key))

    # Asynchronous produce
    producer.produce("webapp",
                     json.dumps(event).encode('utf-8'),
                     key=key.encode('utf-8'),
                     on_delivery=lambda err, msg: delivery_report(err, msg, event))

    # Wait (up to message.timeout.ms) for message to be produced
    # or fail, delivery status is signalled via the delivery_report method
    # that is triggered from this flush() call (or poll()).
    producer.flush()


if __name__ == '__main__':
    # Test
    lambda_handler({'Records': [ { 's3': {
        'bucket': {'name': 'testbucket'},
        'object': {'key': u'testkey'}}} ]}, None)
