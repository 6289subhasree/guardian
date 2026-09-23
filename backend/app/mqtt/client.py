import json
import paho.mqtt.client as mqtt

from app.services.telemetry_service import store_telemetry


MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "guardian/devices/telemetry"


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"MQTT connected | reason_code={reason_code}")
    client.subscribe(MQTT_TOPIC)
    print(f"MQTT subscribed | topic={MQTT_TOPIC}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()

        data = json.loads(payload)

        device_id = data["device_id"]
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])

        telemetry = store_telemetry(
            device_id=device_id,
            temperature=temperature,
            humidity=humidity,
        )

        print(
            f"Telemetry stored | "
            f"device={telemetry.device_id} | "
            f"temperature={telemetry.temperature} | "
            f"humidity={telemetry.humidity} | "
            f"timestamp={telemetry.timestamp}"
        )

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"Invalid telemetry | error={error}")


def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    return client
