#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel

import pika
import json
import threading

# NOTA
# Para rodar, apenas executar no terminal:
# python3 ./payament_service.py

class Payament(BaseModel):
    order_id: int
    payament_approved: bool

class RabbitMQConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pedido_criado', exchange_type='topic')
        
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pedido_criado', queue=queue_name, routing_key='#')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        self.pending_payaments= []
        self.lock = threading.Lock()

    def start_consuming(self):
        print("Started consuming messages.")
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        message = json.loads(body.decode('utf-8'))
        exchange = method.exchange

        if self.lock:
            self.pending_payaments.append(message['order_id'])

        print(self.pending_payaments)
        print(f"Received message from topic '{exchange}': {message}")

    def close_connection(self):
        self.connection.close()


class RabbitMQPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pagamento_aprovado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pagamento_reprovado', exchange_type='topic')

        self.lock = threading.Lock()

    def publish_update_payament_status(self, payament: Payament, exchange_to_send):
        order_id_dict = {
            "order_id": payament.order_id
        }

        json_message = json.dumps(order_id_dict)
        self.channel.basic_publish(exchange=exchange_to_send, routing_key='', body=json_message)
        
        print(f" [x] Sent - publish_update_payament_status: {json_message} to topic {exchange_to_send}")

    def close_connection(self):
        self.connection.close()


##-------------------------- HTTP PART -------------------------#

app = FastAPI()
# Instantiate the RabbitMQPublisher and start consuming in this thread
consumer = RabbitMQConsumer()
publisher = RabbitMQPublisher()

@app.patch("/payament")
def update_payament_status(payament: Payament):
    with consumer.lock:
        if payament.order_id in consumer.pending_payaments:
            exchange_to_send = "pagamento_aprovado" if payament.payament_approved else "pagamento_reprovado"
            publisher.publish_update_payament_status(payament, exchange_to_send)
            consumer.pending_payaments.remove(payament.order_id)
            return {"message": "Payment status updated", "order_id": payament.order_id}
 
    return {"error": "Order ID not found in pending payments"}, 404


def rabbitmq_start():
    consumer.start_consuming()

if __name__ == "__main__":
    import uvicorn
    
    rabbitmq_thread = threading.Thread(target=rabbitmq_start, daemon=True)
    rabbitmq_thread.start()

    uvicorn.run(app, host="127.0.0.1", port=9092)