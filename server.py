import json
import logging
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import ssl
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fhbjbdfughvdfug@547635643'
socketio = SocketIO(app, cors_allowed_origins="*")

# MQTT Configuration
MQTT_BROKER = "2332bf283a3042789deec54af864c4d4.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "admin"
MQTT_PASSWORD = "Admin@123"

# MQTT Topics
TOPIC_COMMAND = "home/switch/command"
TOPIC_STATE = "home/switch/state"
TOPIC_STATUS = "home/switch/status"
TOPIC_AVAILABILITY = "home/switch/availability"

# Global variables to store device state
device_state = {
    'switch_state': 'UNKNOWN',
    'availability': 'offline',
    'last_update': None,
    'device_info': {},
    'connection_status': 'disconnected'
}

# Store recent activity logs
activity_log = deque(maxlen=100)

# MQTT Client
mqtt_client = mqtt.Client()

def add_to_log(message, log_type="info"):
    """Add message to activity log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity_log.appendleft({
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })
    
    # Emit to connected websocket clients
    socketio.emit('log_update', {
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })

def on_connect(client, userdata, flags, rc):
    """Callback for when MQTT client connects"""
    if rc == 0:
        logger.info("Connected to MQTT broker successfully")
        device_state['connection_status'] = 'connected'
        add_to_log("Connected to MQTT broker", "success")
        
        # Subscribe to all topics
        topics = [
            (TOPIC_STATE, 1),
            (TOPIC_STATUS, 1),
            (TOPIC_AVAILABILITY, 1)
        ]
        
        for topic, qos in topics:
            client.subscribe(topic, qos)
            logger.info(f"Subscribed to {topic}")
        
        # Request initial status
        client.publish(TOPIC_COMMAND, "status")
        
        # Emit connection status to websocket clients
        socketio.emit('mqtt_status', {'status': 'connected'})
        
    else:
        logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
        device_state['connection_status'] = 'disconnected'
        add_to_log(f"Failed to connect to MQTT broker (RC: {rc})", "error")
        socketio.emit('mqtt_status', {'status': 'disconnected'})

def on_disconnect(client, userdata, rc):
    """Callback for when MQTT client disconnects"""
    logger.warning("Disconnected from MQTT broker")
    device_state['connection_status'] = 'disconnected'
    add_to_log("Disconnected from MQTT broker", "warning")
    socketio.emit('mqtt_status', {'status': 'disconnected'})

def on_message(client, userdata, msg):
    """Callback for when a message is received"""
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logger.info(f"Received message - Topic: {topic}, Payload: {payload}")
        
        if topic == TOPIC_STATE:
            device_state['switch_state'] = payload
            device_state['last_update'] = datetime.now()
            add_to_log(f"Switch state updated: {payload}")
            
            # Emit state update to websocket clients
            socketio.emit('state_update', {
                'state': payload,
                'timestamp': device_state['last_update'].strftime("%Y-%m-%d %H:%M:%S")
            })
            
        elif topic == TOPIC_STATUS:
            try:
                status_data = json.loads(payload)
                device_state['device_info'] = status_data
                device_state['last_update'] = datetime.now()
                add_to_log("Device status updated")
                
                # Emit status update to websocket clients
                socketio.emit('status_update', status_data)
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in status message: {payload}")
                
        elif topic == TOPIC_AVAILABILITY:
            device_state['availability'] = payload
            add_to_log(f"Device availability: {payload}", 
                      "success" if payload == "online" else "warning")
            
            # Emit availability update to websocket clients
            socketio.emit('availability_update', {'availability': payload})
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        add_to_log(f"Error processing message: {e}", "error")

def setup_mqtt():
    """Setup MQTT client"""
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Setup SSL/TLS
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    mqtt_client.tls_set_context(context)
    
    # Set callbacks
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    
    # Connect to broker
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        logger.info("MQTT client started")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        add_to_log(f"Failed to connect to MQTT broker: {e}", "error")

def send_command(command):
    """Send command to device via MQTT"""
    try:
        if device_state['connection_status'] != 'connected':
            return False, "MQTT not connected"
        
        result = mqtt_client.publish(TOPIC_COMMAND, command)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            add_to_log(f"Command sent: {command}")
            return True, "Command sent successfully"
        else:
            add_to_log(f"Failed to send command: {command}", "error")
            return False, "Failed to send command"
    except Exception as e:
        logger.error(f"Error sending command: {e}")
        add_to_log(f"Error sending command: {e}", "error")
        return False, str(e)

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', 
                         device_state=device_state,
                         activity_log=list(activity_log)[:20])

@app.route('/api/switch/<action>', methods=['POST'])
def control_switch(action):
    """API endpoint to control the switch"""
    valid_actions = ['on', 'off', 'toggle', 'status']
    
    if action not in valid_actions:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    success, message = send_command(action)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 500

@app.route('/api/status')
def get_status():
    """Get current device status"""
    return jsonify({
        'device_state': device_state,
        'activity_log': list(activity_log)[:10]
    })

@app.route('/api/logs')
def get_logs():
    """Get activity logs"""
    return jsonify({'logs': list(activity_log)})

@app.route('/dashboard')
def dashboard():
    """Detailed dashboard page"""
    return render_template('dashboard.html', 
                         device_state=device_state,
                         activity_log=list(activity_log))

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle websocket connection"""
    logger.info("Client connected via WebSocket")
    emit('mqtt_status', {'status': device_state['connection_status']})
    emit('state_update', {
        'state': device_state['switch_state'],
        'timestamp': device_state['last_update'].strftime("%Y-%m-%d %H:%M:%S") if device_state['last_update'] else 'Never'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle websocket disconnection"""
    logger.info("Client disconnected from WebSocket")

@socketio.on('send_command')
def handle_command(data):
    """Handle command from websocket client"""
    command = data.get('command')
    if command:
        success, message = send_command(command)
        emit('command_result', {'success': success, 'message': message})