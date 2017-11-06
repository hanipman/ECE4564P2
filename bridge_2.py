# I used example code provided on the canvas slides
#I used bluetooth code provided by the following

# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $



#!/usr/bin/env python
import pika
import time
import pymongo
import sys
from rmq_params import rmq_params
from pymongo import MongoClient
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

########################################################################################3

db = pymongo.MongoClient().test




credentials2 = pika.PlainCredentials(rmq_params["username"], rmq_params["password"])
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,virtual_host = rmq_params["vhost"], credentials = credentials2 ))
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
while True:
	print("Waiting for connection on RFCOMM channel %d" % port)

	client_sock, client_info = server_sock.accept()
	print("Accepted connection from ", client_info)
	channel.basic_publish(exchange=rmq_params["exchange"],routing_key=rmq_params["status_queue"],body="green")
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
				#severity = "master"
				print(severity)
				if severity in list_queue:
					if (command == "p:"):
						channel.basic_publish(exchange=rmq_params["exchange"],routing_key=severity,body=message)
						time_ = str(time.time())
						#collection = db.test_collection
						#datab = {"Action": command[0], "Place": rmq_params["exchange"],"MsgID": "team_31$"+time_,"Subject": severity, "Message": message}
						#db.utilization.insert(datab)
						print("whats up")
						channel.basic_publish(exchange=rmq_params["exchange"],routing_key=rmq_params["status_queue"],body="purple")
					elif (command == "c:"):
						time_ = str(time.time())
						#db.collection.insert(datab)
						def callback(ch, method, properties, body):
							print("[Checkpoint 03] Consumed a message published with routing_key: '" + method.routing_key + "'")
							print("[Checkpoint 04] Message: " + str(body))
							client_sock.send(str(body))
							
						print("[Checkpoint 02] Consuming messages from '" + rmq_params["master_queue"] + "' queue")
						channel.basic_consume(callback,queue=severity,no_ack=True)
						#Begin consuming
						channel.start_consuming()
						print("consume")
						#datab = {"Action": command[0], "Place": rmq_params["exchange"],"MsgID": "team_31$"+time_,"Subject": severity, "Message": message}
						channel.basic_publish(exchange=rmq_params["exchange"],routing_key=rmq_params["status_queue"],body="yellow")
					elif (command == "h:"):
						#print(collection[0])
						print("print history")
						channel.basic_publish(exchange=rmq_params["exchange"],routing_key=rmq_params["status_queue"],body="blue")
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

	#client_sock.close()
	#server_sock.close()
	#print("all done")

	channel.basic_publish(exchange=rmq_params["exchange"],routing_key=rmq_params["status_queue"],body="red")
	##################################


	#connection.close()
