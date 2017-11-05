#!/usr/bin/env python
import pika
import sys
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(credentials=credentials)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.29.124.160'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

severity = sys.argv[1] if len(sys.argv) > 2 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange='direct_logs',
                      routing_key=severity,
                      body=message)
print(" [x] Sent %r:%r" % (severity, message))
connection.close()
