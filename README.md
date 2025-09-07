## 📄 **README.md**

# MQTT ESP8266 Switch Controller (HTML + WebSocket)

This is a simple and lightweight **HTML + JavaScript MQTT Controller** for controlling an **ESP8266 smart switch** via **HiveMQ Cloud MQTT broker** using **WebSocket (port 8884)**.

No Python, No Flask — pure frontend.

### ESP 8266 CODE
https://github.com/lovnishverma/IOT/blob/mqtt_examples/servo_switch_MQTT.ino

---

## 🚀 **Features**

* Connects to HiveMQ Cloud via MQTT over **WebSocket**.
* Controls switch: `on`, `off`, `toggle`, `status`.
* Displays device state and availability in real-time.
* Clean, responsive UI with modern CSS styling.
* Fully client-side — no backend required.

---

## 🔧 **Configuration**

### HiveMQ Cloud (Example)

```
Broker: 2332bf283xxxxxxxxxx54af864c4d4.s1.eu.hivemq.cloud
Port (WebSocket): 8884
Username: admin
Password: Admin@123
```

### MQTT Topics:

| Purpose             | Topic                      |
| ------------------- | -------------------------- |
| Send Command        | `home/switch/command`      |
| Receive State       | `home/switch/state`        |
| Receive Status      | `home/switch/status`       |
| Device Availability | `home/switch/availability` |

---

## 🛠️ **How to Run**

1. Create a simple `index.html` file.
2. Copy the full HTML code from this project.
3. Open `index.html` directly in your browser.
4. It will connect via **WebSocket 8884** and control your ESP8266 switch.

---

## 📂 **Project Structure**

```
📁 ESP8266-Servo-Switch-Controller-with-MQTT-Integration
 ├── index.html
 └── README.md
```

---

## 🌐 **Demo Screenshot**

![Demo Screenshot](https://github.com/user-attachments/assets/0ff42dc5-5e87-41e4-97f8-41da7de3253a)

---

## 📌 **Notes**

* Ensure your ESP8266 is connected to the same **HiveMQ Cloud broker**.
* Browser must support `wss://` (all modern browsers do).
* **Do not use port `8883` for WebSocket**. Use `8884`.

---

## 📝 **Example Commands**

| Button | MQTT Payload | Topic                 |
| ------ | ------------ | --------------------- |
| ON     | `on`         | `home/switch/command` |
| OFF    | `off`        | `home/switch/command` |
| TOGGLE | `toggle`     | `home/switch/command` |
| STATUS | `status`     | `home/switch/command` |

---

## 📢 **License**

MIT License

---

## 🤝 **Credits**

Developed with ❤️ by [Lovnish Verma](https://lovnishverma.github.io/)
Powered by [HiveMQ Cloud](https://www.hivemq.com/mqtt-cloud-broker/) and [MQTT.js](https://github.com/mqttjs/MQTT.js)


