#!/usr/bin/env python
import pika
import sys
from rmq_params import rmq_params

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

credentials2 = pika.PlainCredentials(rmq_parama["username"], rmq_parama["password"])
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials = credentials2 ))
channel = connection.channel()

channel.exchange_declare(exchange=rmq_params["exchange"],
                         exchange_type='direct')

severity = sys.argv[1] if len(sys.argv) > 2 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

print(" [x] Sent %r:%r" % (severity, message))

###################################################################3

from bluetooth import *

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)
client_sock.send("Communicating on exchange: " + rmq_params["exchange"] + '\n')
client_sock.send("Available Queues:"+ '\n')
count = 0
list_queue = list(rmq_params["queues"])
while count < len(list_queue):
	client_sock.send(list_queue[count]+ '\n')
	count = count + 1
temp = 0
try:
	while True:
		data = client_sock.recv(2048)
		data = str(data)
		if (temp%2 == 0):
			command = data[0] +data[1]
			message = (data.split('"')[1])
			#message = "sup"
			#print(data)
			#print(message)
			severity = data.split(':')[1].split(' ')[0]
			#severity = "what"
			#print(command)
			if severity in list_queue:
				if (command == "p:"):
					channel.basic_publish(exchange='direct_logs',routing_key=severity,body=message)
					#print("whats up")
				elif (command == "c:"):
					print("consume")
				elif (command == "h:"):
					print("print history")
				else:
					print("This is an invalid command")
				if len(data) == 0: break
				#print("received [%s]" % data)
			else:
				print("This queue does not exist")
		temp = temp + 1
except IOError:
    pass

print("disconnected")

client_sock.close()
server_sock.close()
print("all done")


##################################


#connection.close()
