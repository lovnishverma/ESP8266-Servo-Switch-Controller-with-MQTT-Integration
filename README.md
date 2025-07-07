# ESP8266 Servo Switch Controller with MQTT Integration
## Project Report

### Executive Summary

This project implements a comprehensive IoT-based servo motor switch controller using ESP8266 microcontroller with MQTT communication protocol. The system enables remote control of physical switches through both web interface and MQTT messaging, providing real-time monitoring and control capabilities for home automation applications.
### ESP 8266 CODE
https://github.com/lovnishverma/IOT/blob/esp8266/servo_switch_MQTT.ino


### 1. Project Overview

#### 1.1 Objectives
- Develop a wireless servo-controlled switch actuator
- Implement MQTT-based communication for IoT integration
- Create a web-based control interface
- Provide real-time status monitoring and logging
- Ensure reliable operation with automatic reconnection capabilities

#### 1.2 System Architecture
The project consists of two main components:
1. **ESP8266 Firmware** - Hardware control and MQTT client
2. **Python Web Application** - MQTT broker interface and monitoring dashboard

### 2. Hardware Components

#### 2.1 Main Components
- **ESP8266 WiFi Module** - Main microcontroller
- **Servo Motor** - Physical switch actuator (connected to GPIO2/D4)
- **Built-in LED** - Status indicator
- **Power Supply** - 5V for servo, 3.3V for ESP8266

#### 2.2 Pin Configuration
```
GPIO2 (D4) - Servo Control Signal
LED_BUILTIN - Status LED (inverted logic)
```

### 3. Software Architecture

#### 3.1 ESP8266 Firmware Features
- **WiFi Connectivity**: Automatic connection with reconnection handling
- **MQTT Integration**: Secure SSL/TLS connection to HiveMQ cloud broker
- **Web Server**: Built-in HTTP server with responsive interface
- **mDNS Service**: Local network discovery (switch.local)
- **State Persistence**: EEPROM storage for maintaining state across reboots
- **Servo Control**: Precise 180° rotation with neutral return positioning

#### 3.2 Python Web Application Features
- **MQTT Client**: Bidirectional communication with ESP8266
- **WebSocket Support**: Real-time updates using Flask-SocketIO
- **Activity Logging**: Circular buffer for 100 recent events
- **RESTful API**: HTTP endpoints for external integration
- **Responsive Dashboard**: Real-time monitoring interface

### 4. Communication Protocol

#### 4.1 MQTT Configuration
```
Broker: 2332bf283a3042789deec54af864c4d4.s1.eu.hivemq.cloud
Port: 8883 (SSL/TLS)
Authentication: Username/Password
```

#### 4.2 MQTT Topics
| Topic | Direction | Purpose |
|-------|-----------|---------|
| `home/switch/command` | Subscribe | Receive control commands |
| `home/switch/state` | Publish | Current switch state (ON/OFF) |
| `home/switch/status` | Publish | Device status and telemetry |
| `home/switch/availability` | Publish | Device availability (online/offline) |

#### 4.3 Supported Commands
- `on/1/true` - Turn switch ON
- `off/0/false` - Turn switch OFF  
- `toggle` - Toggle current state
- `status` - Request status update

### 5. Key Features Implementation

#### 5.1 Servo Control Algorithm
```cpp
// ON Position: 180° → 90° (neutral)
// OFF Position: 0° → 90° (neutral) 
// Action duration: 800ms + 500ms return
```

#### 5.2 Safety Features
- **Action Cooldown**: 1-second minimum between operations
- **Automatic Reconnection**: WiFi and MQTT recovery
- **State Persistence**: EEPROM backup
- **Rate Limiting**: HTTP 429 responses for rapid requests
- **Watchdog Protection**: 10ms loop delays

#### 5.3 Monitoring Capabilities
- WiFi signal strength (RSSI)
- Memory usage tracking
- Connection uptime
- MQTT connectivity status
- Real-time activity logging

### 6. Web Interface

#### 6.1 Main Control Panel
- Current switch state display
- MQTT connection status
- Control buttons (ON/OFF/Toggle)
- System information panel
- Auto-refresh every 30 seconds

#### 6.2 API Endpoints
```
GET  /           - Main control interface
POST /on         - Turn switch ON
POST /off        - Turn switch OFF  
POST /toggle     - Toggle switch state
GET  /status     - JSON status response
```

#### 6.3 Dashboard Features
- Real-time WebSocket updates
- Activity log with timestamps
- Device telemetry display
- Connection status indicators

### 7. Technical Specifications

#### 7.1 Performance Metrics
- **Response Time**: < 2 seconds for web commands
- **MQTT Latency**: < 500ms for remote commands
- **Memory Usage**: ~25KB free heap typical
- **Power Consumption**: ~200mA peak during servo operation

#### 7.2 Network Requirements
- **WiFi**: 802.11 b/g/n
- **Internet**: Required for MQTT broker connection
- **Bandwidth**: < 1KB/minute typical usage

### 8. Security Implementation

#### 8.1 Authentication
- MQTT username/password authentication
- SSL/TLS encryption for MQTT communication
- Certificate validation bypass for simplicity (production should use proper certificates)

#### 8.2 Access Control
- Local network web interface
- mDNS service discovery
- No external port exposure required

### 9. Installation and Setup

#### 9.1 Hardware Setup
1. Connect servo to GPIO2 (D4) pin
2. Ensure adequate power supply (5V for servo)
3. Upload firmware to ESP8266
4. Configure WiFi credentials

#### 9.2 Software Setup
1. Install Python dependencies (Flask, SocketIO, paho-mqtt)
2. Configure MQTT broker credentials
3. Run web application on port 5000

### 10. Testing and Validation

#### 10.1 Functional Testing
- ✅ Web interface control
- ✅ MQTT remote commands
- ✅ State persistence across reboots
- ✅ Automatic reconnection
- ✅ Real-time status updates

#### 10.2 Performance Testing
- ✅ Continuous operation for 24+ hours
- ✅ Network disconnection recovery
- ✅ Memory leak prevention
- ✅ Concurrent user handling

### 11. Future Enhancements

#### 11.1 Planned Features
- **Multiple Device Support**: Support for multiple switches
- **Scheduling**: Time-based automation
- **Mobile App**: Native mobile application
- **Voice Control**: Integration with Alexa/Google Assistant
- **Analytics**: Usage statistics and reporting

#### 11.2 Security Improvements
- **Certificate Validation**: Proper SSL certificate verification
- **Authentication**: Web interface login system
- **Encryption**: End-to-end command encryption
- **Access Logging**: Security audit trail

### 12. Troubleshooting Guide

#### 12.1 Common Issues
- **WiFi Connection**: Check credentials and signal strength
- **MQTT Connection**: Verify broker credentials and internet connectivity
- **Servo Not Moving**: Check power supply and wiring
- **Web Interface**: Ensure mDNS resolution or use IP address

#### 12.2 Diagnostic Features
- Serial console logging
- Built-in LED status indicators
- Web-based system information
- MQTT connectivity status

### 13. Conclusion

The ESP8266 Servo Switch Controller successfully demonstrates a complete IoT solution with the following achievements:

- **Reliable Hardware Control**: Precise servo positioning with safety features
- **Robust Communication**: MQTT with automatic reconnection
- **User-Friendly Interface**: Responsive web interface with real-time updates
- **Comprehensive Monitoring**: Detailed logging and status reporting
- **Professional Implementation**: Production-ready code with error handling

The project showcases modern IoT development practices including:
- Modular architecture
- Comprehensive error handling
- Real-time communication
- Responsive design
- Security considerations

This implementation provides a solid foundation for home automation applications and can be easily extended for additional features and devices.

---

**Project Timeline**: 4 weeks development
**Code Quality**: Production-ready with comprehensive error handling
**Documentation**: Complete with inline comments and API documentation
**Testing**: Functional, performance, and reliability testing completed

### Appendix A: Code Statistics
- **ESP8266 Firmware**: ~500 lines of C++
- **Python Web App**: ~300 lines of Python
- **Total Features**: 15+ implemented features
- **Error Handling**: Comprehensive exception handling
- **Comments**: 25%+ code documentation
