import json
import logging
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import ssl
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'lovnish@123'
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

# Global state
device_state = {
    'switch_state': 'UNKNOWN',
    'availability': 'offline',
    'last_update': None,
    'device_info': {},
    'connection_status': 'disconnected'
}
activity_log = deque(maxlen=100)

# MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.enable_logger()

# Log Helper
def add_to_log(message, log_type="info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activity_log.appendleft({
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })
    socketio.emit('log_update', {
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to MQTT broker")
        device_state['connection_status'] = 'connected'
        add_to_log("Connected to MQTT broker", "success")
        socketio.emit('mqtt_status', {'status': 'connected'})

        client.subscribe([(TOPIC_STATE, 1), (TOPIC_STATUS, 1), (TOPIC_AVAILABILITY, 1)])
        client.publish(TOPIC_COMMAND, "status")
    else:
        logger.error(f"❌ Failed to connect, return code: {rc}")
        device_state['connection_status'] = 'disconnected'
        add_to_log(f"Failed to connect (RC: {rc})", "error")
        socketio.emit('mqtt_status', {'status': 'disconnected'})

def on_disconnect(client, userdata, rc):
    logger.warning("⚠️ Disconnected from MQTT broker")
    device_state['connection_status'] = 'disconnected'
    add_to_log("Disconnected from MQTT broker", "warning")
    socketio.emit('mqtt_status', {'status': 'disconnected'})

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        logger.info(f"📩 {topic} -> {payload}")

        if topic == TOPIC_STATE:
            device_state['switch_state'] = payload
            device_state['last_update'] = datetime.now()
            add_to_log(f"Switch state updated: {payload}")
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
                socketio.emit('status_update', status_data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in status: {payload}")

        elif topic == TOPIC_AVAILABILITY:
            device_state['availability'] = payload
            add_to_log(f"Device is {payload}", "success" if payload == "online" else "warning")
            socketio.emit('availability_update', {'availability': payload})

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        add_to_log(f"Error processing message: {e}", "error")

# MQTT Setup
def setup_mqtt():
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    mqtt_client.tls_set_context(context)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        logger.info("MQTT client loop started")

        for _ in range(10):
            if device_state['connection_status'] == 'connected':
                logger.info("✅ MQTT ready")
                break
            time.sleep(1)
        else:
            logger.warning("MQTT not connected after timeout")

    except Exception as e:
        logger.error(f"MQTT connection failed: {e}")
        add_to_log(f"MQTT connection failed: {e}", "error")

# Command Sender
def send_command(command):
    try:
        if device_state['connection_status'] != 'connected' and not mqtt_client.is_connected():
            return False, "MQTT not connected"

        result = mqtt_client.publish(TOPIC_COMMAND, command)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            add_to_log(f"✅ Command sent: {command}")
            return True, "Command sent"
        else:
            add_to_log(f"❌ Failed to send command: {command}", "error")
            return False, "Failed to send command"

    except Exception as e:
        logger.error(f"Command error: {e}")
        add_to_log(f"Command error: {e}", "error")
        return False, str(e)

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html',
                           device_state=device_state,
                           activity_log=list(activity_log)[:20])

@app.route('/api/switch/<action>', methods=['POST'])
def control_switch(action):
    if action not in ['on', 'off', 'toggle', 'status']:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400

    success, message = send_command(action)
    return jsonify({'success': success, 'message': message}), (200 if success else 500)

@app.route('/api/status')
def get_status():
    return jsonify({
        'device_state': device_state,
        'activity_log': list(activity_log)[:10]
    })

@app.route('/api/logs')
def get_logs():
    return jsonify({'logs': list(activity_log)})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',
                           device_state=device_state,
                           activity_log=list(activity_log))

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    logger.info("WebSocket connected")
    emit('mqtt_status', {'status': device_state['connection_status']})
    emit('state_update', {
        'state': device_state['switch_state'],
        'timestamp': device_state['last_update'].strftime("%Y-%m-%d %H:%M:%S") if device_state['last_update'] else 'Never'
    })

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("WebSocket disconnected")

@socketio.on('send_command')
def handle_command(data):
    command = data.get('command')
    if command:
        success, message = send_command(command)
        emit('command_result', {'success': success, 'message': message})

# Run
if __name__ == '__main__':
    setup_mqtt()
    socketio.run(app, host='0.0.0.0', port=5000)
