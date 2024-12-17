#!/usr/bin/env python3
from fastapi import FastAPI
from stock_json_helper import StockJsonHelper

import pika
import json
import threading

# NOTA
# Para rodar, apenas executar no terminal:
# python3 ./stock_service.py

##-------------------------- RabbitMQ PART -------------------------#
class RabbitMQPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pedido_criado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pedido_excluido', exchange_type='topic')

        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pedido_criado', queue=queue_name, routing_key='#')
        self.channel.queue_bind(exchange='pedido_excluido', queue=queue_name, routing_key='#')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)

    def start_consuming(self):
        print("Started consuming messages.")
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        message = body.decode('utf-8')
        exchange = method.exchange

        data = json.loads(message)
        stock_id = data['stock_id']
        quantity = data['quantity']
        stock_exists = StockJsonHelper.verify_stock_by_id(stock_id)

        if exchange == 'pedido_criado':    
            if (stock_exists):
                StockJsonHelper.decrease_stock(stock_id, quantity)
        else:
            if (stock_exists):
                StockJsonHelper.increase_stock(stock_id, quantity)
        print(f"Received message from topic '{exchange}': {message}")

    def close_connection(self):
        self.connection.close()

##-------------------------- HTTP PART -------------------------#

app = FastAPI()

@app.get("/stock")
def get_stock():
    stock_data = StockJsonHelper.read_all_stock()
    return stock_data

def rabbitmq_consumer():
    # Instantiate the RabbitMQPublisher and start consuming in this thread
    publisher = RabbitMQPublisher()
    publisher.start_consuming()

if __name__ == "__main__":
    import uvicorn
    
    rabbitmq_thread = threading.Thread(target=rabbitmq_consumer, daemon=True)
    rabbitmq_thread.start()

    uvicorn.run(app, host="127.0.0.1", port=9091)
