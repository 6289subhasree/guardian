// Flash the same sketch to each board with a distinct DEVICE_ID.
// Install the PubSubClient library through Arduino Library Manager.
#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>

const char* WIFI_SSID = "YOUR_LAB_WIFI";
const char* WIFI_PASSWORD = "YOUR_LAB_PASSWORD";
const char* SERVER_IP = "192.168.1.10";  // Laptop IPv4 address on lab network
const char* DEVICE_ID = "ESP32-001";
const char* TOPIC = "guardian/devices/telemetry";

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
unsigned long lastPublished = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(WiFi.localIP());
  mqtt.setServer(SERVER_IP, 1883);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(1000);
    return;
  }
  if (!mqtt.connected()) {
    mqtt.connect(DEVICE_ID);
  }
  mqtt.loop();
  if (millis() - lastPublished < 5000) return;
  lastPublished = millis();

  // Fixed demonstration values. Replace with physical sensor readings if available.
  String payload = String("{\"device_id\":\"") + DEVICE_ID +
                   "\",\"temperature\":25.0,\"humidity\":50.0}";
  mqtt.publish(TOPIC, payload.c_str());

  HTTPClient http;
  String url = String("http://") + SERVER_IP + ":8000/devices/" + DEVICE_ID + "/heartbeat";
  http.begin(url);
  int status = http.POST("");
  Serial.printf("MQTT=%d heartbeat=%d\n", mqtt.connected(), status);
  http.end();
}
