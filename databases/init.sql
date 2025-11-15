-- Initialisation PostgreSQL
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, email, password_hash) VALUES
    ('john_doe', 'john@example.com', 'hashed_password_123'),
    ('jane_smith', 'jane@example.com', 'hashed_password_456')
ON CONFLICT (username) DO NOTHING;

INSERT INTO products (name, price, description) VALUES
    ('Laptop', 999.99, 'High performance laptop'),
    ('Smartphone', 699.99, 'Latest smartphone model'),
    ('Headphones', 199.99, 'Noise-cancelling headphones')
ON CONFLICT (name) DO NOTHING;  