import pika
import sys
from rmq_params import rmq_params

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=rmq_params["exchange"],exchange_type='direct')

result = channel.queue_declare(queue=rmq_params["master_queue"])
queue_name = result.method.queue
channel.queue_purge(queue_name)
channel.queue_unbind(queue=queue_name, exchange=rmq_params["exchange"], routing_key=queue_name)
channel.queue_bind(exchange=rmq_params["exchange"], queue=queue_name, routing_key=queue_name)

result = channel.queue_declare(queue=rmq_params["status_queue"])
queue_name = result.method.queue
channel.queue_purge(queue_name)
channel.queue_unbind(queue=queue_name, exchange=rmq_params["exchange"], routing_key=queue_name)
channel.queue_bind(exchange=rmq_params["exchange"], queue=queue_name, routing_key=queue_name)

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

print(' Waiting for messages.' )

def callback(ch, method, properties, body):
    print(" [x] %r" % body)

channel.basic_consume(callback,
                      queue=rmq_params["master_queue"],
                      no_ack=True)

channel.start_consuming()
