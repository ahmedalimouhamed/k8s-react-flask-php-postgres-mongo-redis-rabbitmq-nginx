import React, {useState, useEffect} from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [users, setUsers] = useState([]); 
  const [health, setHealth] = useState({});

  useEffect(() => {
    fetchHealth();
    fetchUsers();
  }, []);

  const fetchHealth = async () => { 
    try {
      const response = await axios.get(`${API_URL}/health`);
      setHealth(response.data);
    } catch(error) {
      console.error("Health check failed: ", error); 
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/users`);
      setUsers(response.data);
    } catch(error) {
      console.error('Failed to fetch users: ', error);
    }
  };

  const createOrder = async () => {
    try {
      const orderData = {
        user_id: 1,
        total: 99.99,
        items: ['product1', 'product2'], 
        metadata: {source: 'web'} 
      };
      await axios.post(`${API_URL}/orders`, orderData);
      alert('Order created successfully!');
    } catch(error) {
      console.error('Failed to create order: ', error);
    }
  };

  return (
    <div>
      <h1>Multi-Stack Application</h1>

      <div>
        <h2>Service Health</h2>
        <div>
          PostgreSQL: {health.postgres ? 'OK' : 'X'} |
          MongoDB: {health.mongodb ? 'OK' : 'X'} | {}
          Redis: {health.redis ? 'OK' : 'X'} | {}
          RabbitMQ: {health.rabbitmq ? 'OK' : 'X'} {}
        </div>
      </div>

      <button onClick={createOrder}>Create Test Order</button>

      <div>
        <h2>Users</h2>
        <ul>
          {users.map(user => (
            <li key={user.id}>{user.name} - {user.email}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;