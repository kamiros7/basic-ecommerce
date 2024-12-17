#!/usr/bin/env python3

# NOTA
# Para executar, no terminal apenas rodar:
#  python3 ./deilvery_service.py
import pika

##-------------------------- RabbitMQ PART -------------------------#
class RabbitMQPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pagamento_aprovado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pedido_enviado', exchange_type='topic')

        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pagamento_aprovado', queue=queue_name, routing_key='#')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)

    def start_consuming(self):
        print("Started consuming messages.")
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        message = body.decode('utf-8')
        exchange = method.exchange
        self.publish_order_sent(body)

        print(f"Received message from topic '{exchange}': {message}")

    def publish_order_sent(self, message):
        self.channel.basic_publish(exchange='pedido_enviado', routing_key='', body=message)
        
        print(" [x] Sent publish_order_sent:")


    def close_connection(self):
        self.connection.close()

# Initialize RabbitMQ publisher
publisher = RabbitMQPublisher()

if __name__ == "__main__":
    
    publisher.start_consuming()