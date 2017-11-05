#!/usr/bin/env python
import pika
import sys

# https://gist.github.com/didler/2395703 {
def getopts(argv):
	opts ={}
	while sys.argv:
		if sys.argv[0][0] == '-':
			opts[sys.argv[0]] = sys.argv[1]
		sys.argv = sys.argv[1:]
	return opts

myargs = getopts(sys.argv)
if not myargs:
	print('No arguments found')
	sys.exit()
if '-s' in myargs:
	host = myargs['-s']
	myargs.pop('-s', None)
if len(myargs.keys()) != 0:
	print('Invalid arguments')
	sys.exit()
# }


credentials2 = pika.PlainCredentials(host, 'raspberry')
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
