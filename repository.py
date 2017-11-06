import pika
import sys
from rmq_params import rmq_params

#Create the channel
cred = pika.PlainCredentials('pi', 'raspberry')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', virtual_host='test', credentials=cred))
channel = connection.channel()
print("[Checkpoint 01] Connected to vhost '" + rmq_params["vhost"] + "' on RMQ server at 'localhost' as user '" + rmq_params["username"] + "'")

#Declare Exchange
channel.exchange_declare(exchange=rmq_params["exchange"],exchange_type='direct')

#Create Master queue and bind it to exchange
result = channel.queue_declare(queue=rmq_params["master_queue"])
queue_name = result.method.queue
channel.queue_purge(queue_name)
channel.queue_unbind(queue=queue_name, exchange=rmq_params["exchange"], routing_key=queue_name)
channel.queue_bind(exchange=rmq_params["exchange"], queue=queue_name, routing_key=queue_name)

#Create Status queue and bind it to exchange
#Also binds master queue to exchange
result = channel.queue_declare(queue=rmq_params["status_queue"])
queue_name = result.method.queue
channel.queue_purge(queue_name)
channel.queue_unbind(queue=queue_name, exchange=rmq_params["exchange"], routing_key=queue_name)
channel.queue_bind(exchange=rmq_params["exchange"], queue=queue_name, routing_key=queue_name)

#Creates a queue for every item in the queues set and binds it to the exchange
#Also creates binds the master queue to every new routing key
count = 0
list_queue = list(rmq_params["queues"])
while count < len(list_queue):
	result = channel.queue_declare(queue=list_queue[count])
	queue_name = result.method.queue
	channel.queue_purge(queue_name)
	channel.queue_unbind(queue=queue_name, exchange=rmq_params["exchange"], routing_key=queue_name)
	channel.queue_bind(exchange=rmq_params["exchange"], queue=queue_name, routing_key=queue_name)
	channel.queue_bind(exchange=rmq_params["exchange"], queue=rmq_params["master_queue"], routing_key=queue_name)
	count = count + 1

#Wait for messages
def callback(ch, method, properties, body):
    print("[Checkpoint 03] Consumed a message published with routing_key: '" + method.routing_key + "'")
    print("[Checkpoint 04] Message: " + str(body))
    if str(body) == 'red':
        print("[Checkpoint 1-01] Flashing LED red")
    elif str(body) == 'green':
        print("[Checkpoint 1-01] Flashing LED green")
    elif str(body) == 'blue':
        print("[Checkpoint 1-01] Flashing LED blue")
    elif str(body) == 'white':
        print("[Checkpoint 1-01] Flashing LED white")

print("[Checkpoint 02] Consuming messages from '" + rmq_params["master_queue"] + "' queue")
channel.basic_consume(callback,
                      queue=rmq_params["master_queue"],
                      no_ack=True)

#Begin consuming
channel.start_consuming()

