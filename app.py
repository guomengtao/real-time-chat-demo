# Import required libraries
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import redis
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, async_mode='threading', logger=True, engineio_logger=True)

# Connect to Redis
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    redis_client.ping()
    logger.info("Successfully connected to Redis")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")

# Route for the main page
@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

# Handle WebSocket connection
@socketio.on('connect')
def handle_connect():
    logger.info("New client connected")
    try:
        # Load last 50 messages from Redis
        messages = []
        for message in redis_client.lrange('messages', 0, 49):
            messages.append(json.loads(message))
        emit('load_messages', messages)
        logger.info(f"Sent {len(messages)} messages to new client")
    except Exception as e:
        logger.error(f"Error loading messages: {e}")

# Handle new messages
@socketio.on('new_message')
def handle_message(data):
    logger.info(f"Received new message from {data.get('user')}")
    try:
        # Create message object
        message = {
            'user': data['user'],
            'message': data['message'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store message in Redis
        redis_client.lpush('messages', json.dumps(message))
        redis_client.ltrim('messages', 0, 99)  # Keep only last 100 messages
        
        # Broadcast message to all connected clients
        emit('new_message', message, broadcast=True)
        logger.info("Message broadcasted successfully")
    except Exception as e:
        logger.error(f"Error handling message: {e}")

if __name__ == '__main__':
    logger.info("Starting Flask-SocketIO server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 