#!/usr/bin/env python3

# NOTA
# Para executar, rodar o script: 
# python3 ./payament_integrated_system.py 1 1
# Em que o primeiro inteiro é o order_id
# E o segundo inteiro indica se o pagamento será aprovado ou não
# No qual 0, significa reprovado e 1 para aprovado

import sys
import httpx

def send_payament(order_id, payament_approved):
    url = "http://localhost:9092/payament"

    payload = {
        "order_id": order_id,
        "payament_approved": payament_approved
    }
    
    with httpx.Client() as client:
        response = client.patch(url, json=payload)

    print(f"Response from payament service: {response}")

if __name__ == "__main__":
    order_id = sys.argv[1]
    payament_approved = True if sys.argv[2] == '1' else False
    response = send_payament(order_id, payament_approved)
    