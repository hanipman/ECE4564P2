#!/usr/bin/env python
import pika
import sys
credentials2 = pika.PlainCredentials('pi', 'raspberry')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.29.124.160',credentials = credentials2 ))
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
