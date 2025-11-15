import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import pymongo
import redis
import pika
import json
import os

app = Flask(__name__)
CORS(app) 

# Configurations
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgres:5432')
#MONGO_URL = os.getenv('MONGO_URL', 'mongodb:27017')
MONGO_URL = 'mongodb:27017'
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
#RABBITMQ_HOST = os.getenv('RABBITMQ_URL', 'rabbitmq')
RABBITMQ_HOST = 'rabbitmq'

# DEBUG - Afficher les valeurs des variables d'environnement
print("=== DEBUG ENV VARIABLES ===")
print(f"MONGO_URL: '{MONGO_URL}'")
print(f"POSTGRES_URL: '{POSTGRES_URL}'")
print(f"REDIS_HOST: '{REDIS_HOST}'")
print(f"RABBITMQ_HOST: '{RABBITMQ_HOST}'")
print("===========================")

# Connexion bases de données
def get_postgres_conn():
    return psycopg2.connect(f"postgresql://appuser:apppass@{POSTGRES_URL}/appdb")

def get_mongo_client():
    mongo_uri = f"mongodb://{MONGO_URL}/appdb"
    return pymongo.MongoClient(mongo_uri)

def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials("guest", "guest")
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=5672, credentials= credentials)
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
        return jsonify(users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        
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
        mongo_db = mongo_client.appdb
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
        channel.queue_declare(
            queue='order_created', 
            durable=True, 
            auto_delete=False,
            arguments=None
        )
        channel.basic_publish(
            exchange='',
            routing_key='order_created',
            body=json.dumps({'order_id': order_id, 'user_id': data['user_id']})
        )
        connection.close()

        return jsonify({'order_id': order_id, 'status': 'created'})
    
    except Exception as e:
        print("Error creating order: ", e)
        traceback.print_exc()  
        return jsonify({'error': str(e)}), 500

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