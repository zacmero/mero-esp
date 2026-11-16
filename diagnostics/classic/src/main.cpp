#include <Arduino.h>
#include <BluetoothSerial.h>
#include <esp_bt_device.h>

BluetoothSerial bluetooth;
size_t echoed = 0;

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.printf("CHIP %s REV %d FLASH_BYTES %u\n", ESP.getChipModel(),
                ESP.getChipRevision(), ESP.getFlashChipSize());
  if (!bluetooth.begin("MERO-ESP32-CLASSIC")) {
    Serial.println("CLASSIC_INIT FAIL");
    return;
  }
  const uint8_t *address = esp_bt_dev_get_address();
  Serial.printf("CLASSIC_READY %02X:%02X:%02X:%02X:%02X:%02X\n",
                address[0], address[1], address[2], address[3], address[4], address[5]);
}

void loop() {
  uint8_t buffer[128];
  size_t count = 0;
  while (bluetooth.available() && count < sizeof(buffer)) {
    buffer[count++] = static_cast<uint8_t>(bluetooth.read());
  }
  if (count) {
    bluetooth.write(buffer, count);
    echoed += count;
    Serial.printf("CLASSIC_ECHO_BYTES %u\n", static_cast<unsigned>(echoed));
  }
  delay(2);
}
