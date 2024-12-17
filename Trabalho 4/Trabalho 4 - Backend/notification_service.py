#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import pika
import asyncio
import threading
import json

# NOTA
# Para rodar, apenas executar no terminal:
# python3 ./notification_service.py

##-------------------------- RabbitMQ PART -------------------------#
class RabbitMQConsumer:
    def __init__(self, message_queue):
        self.message_queue = message_queue

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pagamento_aprovado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pagamento_reprovado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pedido_enviado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pedido_criado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pedido_excluido', exchange_type='topic')

        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pagamento_aprovado', queue=queue_name, routing_key='#')
        self.channel.queue_bind(exchange='pagamento_reprovado', queue=queue_name, routing_key='#')
        self.channel.queue_bind(exchange='pedido_enviado', queue=queue_name, routing_key='#')
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
        order_id = data['order_id']

        print(f"Received message from topic '{exchange}': {message}")
        sse_message = {"order_id": order_id, "status": exchange}

        asyncio.run(self.message_queue.put(sse_message))
        

##-------------------------- HTTP PART -------------------------#

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins. Replace "*" with specific domains if needed.
    allow_methods=["GET"],  # Allow only GET requests
    allow_headers=["*"],  # Allow all headers
)

message_queue = asyncio.Queue()

async def event_stream():
    while True:
        message = await message_queue.get()
        json_message = json.dumps(message)
        yield f"data: {json_message}\n\n"

# SSE endpoint
@app.get("/sse")
async def sse_endpoint():
    return StreamingResponse(event_stream(), media_type="text/event-stream")

def start_rabbitmq_consumer():
    consumer = RabbitMQConsumer(message_queue)
    consumer.start_consuming()


if __name__ == "__main__":
    import uvicorn

    rabbitmq_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    rabbitmq_thread.start()

    uvicorn.run(app, host="127.0.0.1", port=9093)