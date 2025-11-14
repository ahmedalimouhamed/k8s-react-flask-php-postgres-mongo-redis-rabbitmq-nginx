from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import pymongo
import redis
import pika
import json
import os

app = Flask(__name__)
CORS(app)  # Cela devrait normalement résoudre les problèmes CORS

# Configurations
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

# Connexion bases de données
def get_postgres_conn():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database="mydb",
        user="user",
        password="pass",
        port=5432
    )

def get_mongo_client():
    return pymongo.MongoClient(f"mongodb://{MONGO_HOST}:27017/")

def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)  # Correction: Redis au lieu de Rdis

def get_rabbitmq_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=5672)
    )

# Routes API
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convertir en format JSON propre
        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'name': user[1],
                'email': user[2]
            })
        return jsonify(users_list)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json() 
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # PostgreSQL - données transactionnelles
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (user_id, total) VALUES(%s, %s) RETURNING id",  
            (data['user_id'], data['total'])
        )
        order_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        # MongoDB - données document
        mongo_client = get_mongo_client()
        mongo_db = mongo_client.mydb
        mongo_db.orders.insert_one({
            'postgres_id': order_id,
            'items': data['items'],
            'metadata': data.get('metadata', {})
        })
        mongo_client.close()

        # Redis - cache
        redis_client = get_redis_client()
        redis_client.set(f"order:{order_id}", json.dumps(data))

        # RabbitMQ - notification
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue='order_created')
        channel.basic_publish(
            exchange='',
            routing_key='order_created',
            body=json.dumps({'order_id': order_id, 'user_id': data['user_id']})
        )
        connection.close()

        return jsonify({'order_id': order_id, 'status': 'created'})
    
    except Exception as e:
        print(f"Error creating order: {e}")
        return jsonify({'error': 'Failed to create order'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    services = {
        'postgres': False,
        'mongodb': False,
        'redis': False,
        'rabbitmq': False
    }

    try:
        conn = get_postgres_conn()
        conn.close()
        services['postgres'] = True
    except Exception as e:
        print(f"PostgreSQL health check failed: {e}")

    try:
        mongo_client = get_mongo_client()
        mongo_client.admin.command('ismaster')
        services['mongodb'] = True
        mongo_client.close()
    except Exception as e:
        print(f"MongoDB health check failed: {e}")

    try:
        redis_client = get_redis_client()
        redis_client.ping()
        services['redis'] = True
    except Exception as e:
        print(f"Redis health check failed: {e}")

    try:
        connection = get_rabbitmq_connection()
        connection.close()
        services['rabbitmq'] = True
    except Exception as e:
        print(f"RabbitMQ health check failed: {e}")

    return jsonify(services)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)