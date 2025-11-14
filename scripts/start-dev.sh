#!/bin/bash
echo "Starting development environment..."

# Démarrage des conteneurs Docker
docker run -d --name postgres-dev \
    -e POSTGRES_USER=user \
    -e POSTGRES_PASSWORD=pass \
    -e POSTGRES_DB=mydb \
    -p 5432:5432 \
    postgres:15

docker run -d --name mongodb-dev \
    -p 27017:27017 \
mongo:6

docker run -d --name redis-dev \
    -p 6379:6379 \
redis:7-alpine

docker run -d --name rabbitmq-dev \
    -p 5672:5672 -p 15672:15672 \
rabbitmq:3-management

echo "Waiting for services to start..."
sleep 10

# Initialisation de la base PostgreSQL
docker exec -i postgres-dev psql -U user -d mydb << EOF
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    );

    CREATE TABLE IF NOT EXISTS orders(
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        total DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT NOW()
    );

    INSERT INTO users (name, email) VALUES
        ('John Doe', 'john@example.com'),
        ('Jane Smith', 'jane@example.com');
EOF

# Démarrage du backend Flask
cd backend-api
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python app.py & 
FLASK_PID=$!

# Démarrage du service PHP
cd ../backend-services
if [ ! -f "composer.lock" ]; then
    composer install
fi

php src/NotificationService.php &
PHP_PID=$!

# Démarrage du frontend
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

npm start & 
FRONTEND_PID=$!

echo "All services started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:5000"
echo "RabbitMQ Management: http://localhost:15672 (guest/guest)"

# Arrêt propre des services
trap "kill $FLASK_PID $PHP_PID $FRONTEND_PID 2>/dev/null; docker stop postgres-dev mongodb-dev redis-dev rabbitmq-dev; docker rm postgres-dev mongodb-dev redis-dev rabbitmq-dev" EXIT

wait