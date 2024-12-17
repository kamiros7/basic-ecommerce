from pydantic import BaseModel
from fastapi import FastAPI
from typing import Optional
from order_json_helper import OrderJsonHelper

import pika
import json
import httpx
import threading

# NOTA
# Para rodar, apenas executar no terminal:
# python3 ./main_service.py

class Order(BaseModel):
    order_id: int
    item: str #essa variavel não está sendo usada, necessária apenas pro stock
    quantity: int
    client_id : int #essa variavel não está sendo usada
    stock_id: int
    status: Optional[str] = None

##-------------------------- RabbitMQ PART -------------------------#
class RabbitMQPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pedido_criado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pedido_excluido', exchange_type='topic')

    def publish_created_order(self, order):
        filtered_order_dict = {
            "stock_id": order['stock_id'],
            "quantity": order['quantity'],
            "order_id": order['order_id']
        }
        json_message = json.dumps(filtered_order_dict)
        message_body = json_message.encode('utf-8')
        self.channel.basic_publish(exchange='pedido_criado', routing_key='', body=message_body)
        
        print(" [x] Sent publish_created_order:", json_message)

    def publish_deleted_order(self, order):
        deleted_order = {
            "stock_id": order["stock_id"],
            "quantity": order["quantity"],
            "order_id": order['order_id']
        }
        json_message = json.dumps(deleted_order)
        message_body = json_message.encode('utf-8')
        self.channel.basic_publish(exchange='pedido_excluido', routing_key='', body=message_body)
        print(" [x] Sent publish_deleted_order:", json_message)

    def close_connection(self):
        self.connection.close()


class RabbitMQConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pagamento_aprovado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pagamento_reprovado', exchange_type='topic')
        self.channel.exchange_declare(exchange='pedido_enviado', exchange_type='topic')
        
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pagamento_aprovado', queue=queue_name, routing_key='#')
        self.channel.queue_bind(exchange='pagamento_reprovado', queue=queue_name, routing_key='#')
        self.channel.queue_bind(exchange='pedido_enviado', queue=queue_name, routing_key='#')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)

    def callback(self, ch, method, properties, body):
        message = body.decode('utf-8')
        exchange = method.exchange
        print(f"Received message from topic '{exchange}': {message}")

        message = body.decode('utf-8')
        exchange = method.exchange

        data = json.loads(message)
        order_id = data['order_id']
        order_exists = OrderJsonHelper.verify_order_by_id(order_id)
        if order_exists:
            if exchange == 'pagamento_aprovado':
                OrderJsonHelper.update_order_status(order_id, 'approved_payament')
            elif exchange == 'pagamento_reprovado':
                OrderJsonHelper.update_order_status(order_id, 'disapproved_payament')
                order = OrderJsonHelper.get_item_by_id(order_id)
                publisher.publish_deleted_order(order)
            else:
                OrderJsonHelper.update_order_status(order_id, 'delivery_sent')

    def start_consuming(self):
        self.channel.start_consuming()

    def close_connection(self):
        self.connection.close()


# Initialize RabbitMQ publisher
publisher = RabbitMQPublisher()
consumer = RabbitMQConsumer()
##-------------------------- HTTP PART -------------------------#

app = FastAPI()

@app.get("/stock")
async def get_stock():
    url = "http://localhost:9091/stock"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    stock = response.json()
    return {"stock": stock}

@app.get("/orders")
def get_orders():
    orders = OrderJsonHelper.read_all_orders()
    return {"orders": orders}

@app.post("/order")
def create_order(order: Order):
    #impossibilitar de criar order com mesmo ID
    order.status = 'pending_payament'
    order_dict = order.model_dump()
    OrderJsonHelper.add_order(order_dict)
    publisher.publish_created_order(order_dict)
    return {"Message" : "Order created"}

@app.delete("/order/{order_id}")
def delete_order(order_id: int):
    order = OrderJsonHelper.get_item_by_id(order_id)
    publisher.publish_deleted_order(order)
    OrderJsonHelper.delete_order_by_id(order_id)
    return {"Message": f"order deleted : {order_id}"}

def rabbitmq_start():
    consumer.start_consuming()

if __name__ == "__main__":
    import uvicorn

    rabbitmq_thread = threading.Thread(target=rabbitmq_start, daemon=True)
    rabbitmq_thread.start()

    uvicorn.run(app, host="127.0.0.1", port=9090)
