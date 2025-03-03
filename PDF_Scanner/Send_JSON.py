import requests
import json

url = "https://a256-106-51-110-167.ngrok-free.app/api/product"
headers = {"Content-Type": "application/json"}
data = {
    "name": "Organic Apples",
    "price": 2.99,
    "category": "Fruits",
    "stock": 100
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())