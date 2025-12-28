#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "SEU_WIFI";
const char* password = "SUA_SENHA";

WebServer server(80);
const int ledPin = 2;

void ledOn() {
  digitalWrite(ledPin, HIGH);
  server.send(200, "text/plain", "LED ON");
}

void ledOff() {
  digitalWrite(ledPin, LOW);
  server.send(200, "text/plain", "LED OFF");
}

void status() {
  server.send(200, "text/plain", "ESP32 ONLINE");
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Serial.println(WiFi.localIP());

  server.on("/on", ledOn);
  server.on("/off", ledOff);
  server.on("/status", status);

  server.begin();
}

void loop() {
  server.handleClient();
}
