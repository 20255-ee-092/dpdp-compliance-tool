from flask import Flask, jsonify, request
import json
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/api/product', methods=['GET'])
def get_product():
    with open('Organic-Product-Details.json', 'r') as file:
        product_data = json.load(file)
    return jsonify(product_data)

@app.route('/api/product', methods=['POST'])
def save_product():
    try:
        # Check if the request contains JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        # Get the JSON data from the request
        product_data = request.get_json()

        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        filename = f'product_data_{timestamp}.json'

        # Save the JSON data to a file
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(product_data, file, indent=4, ensure_ascii=False)

        return jsonify({'message': 'Data saved successfully', 'filename': filename}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
