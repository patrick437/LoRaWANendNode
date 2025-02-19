import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from LoRaRF import SX126x
import time
import struct
import random

# AWS IoT Core LoRaWAN credentials
DEVEUI = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Replace with your DevEUI
APPEUI = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Replace with your AppEUI
APPKEY = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Replace with your AppKey
         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

# Initialize LoRa radio
busId = 0
csId = 0
resetPin = 18
busyPin = 20
irqPin = 16
txenPin = 6
rxenPin = -1

LoRa = SX126x()
print("Initializing LoRa radio...")
if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin):
    raise Exception("Failed to initialize LoRa radio")

# Configure radio parameters
LoRa.setDio2RfSwitch()
LoRa.setFrequency(868100000)  # EU868 Channel 0
print("Set frequency to 868.1 MHz")

# Set TX power
LoRa.setTxPower(14, LoRa.TX_POWER_SX1262)  # 14 dBm is standard for LoRaWAN
print("Set TX power to +14 dBm")

# Configure LoRaWAN parameters
sf = 7
bw = 125000
cr = 5
LoRa.setLoRaModulation(sf, bw, cr)
print(f"Set modulation parameters:\n\tSF = {sf}\n\tBW = {bw} Hz\n\tCR = 4/{cr}")

# Set packet parameters
headerType = LoRa.HEADER_EXPLICIT  # LoRaWAN uses explicit header
preambleLength = 8
payloadLength = 255  # Max payload length for flexibility
crcType = True
LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType)
print("Packet parameters configured")

# Initialize LoRaWAN
print("\n-- LoRaWAN Node Starting --\n")
LoRa.setLoRaWAN()  # Set radio to LoRaWAN mode
LoRa.setDeviceEUI(DEVEUI)
LoRa.setApplicationEUI(APPEUI)
LoRa.setApplicationKey(APPKEY)

# Join the network
print("Attempting to join LoRaWAN network...")
join_attempts = 0
max_join_attempts = 5

while join_attempts < max_join_attempts:
    if LoRa.join():
        print("Successfully joined the network!")
        break
    else:
        join_attempts += 1
        print(f"Join failed (attempt {join_attempts}/{max_join_attempts}), retrying...")
        time.sleep(5)

if join_attempts >= max_join_attempts:
    raise Exception("Failed to join network after maximum attempts")

# Main sending loop
message_counter = 0
try:
    while True:
        # Prepare sensor data (example with temperature and humidity)
        temperature = random.uniform(20.0, 25.0)  # Replace with actual sensor reading
        humidity = random.uniform(40.0, 60.0)     # Replace with actual sensor reading
        
        # Pack data into bytes
        data = struct.pack('ff', temperature, humidity)
        
        print(f"\nSending message {message_counter}")
        print(f"Temperature: {temperature:.1f}°C")
        print(f"Humidity: {humidity:.1f}%")
        
        # Send data
        if LoRa.send(data):
            print("Data sent successfully!")
            print(f"Transmit time: {LoRa.transmitTime():.2f} ms")
        else:
            print("Failed to send data")
            if LoRa.status() == LoRa.STATUS_TX_TIMEOUT:
                print("Transmit timeout")
        
        message_counter += 1
        
        # Sleep between transmissions (e.g., 5 minutes)
        LoRa.sleep()
        time.sleep(300)  # Adjust this based on your needs and duty cycle requirements
        LoRa.wake()

except KeyboardInterrupt:
    print("\nStopping LoRaWAN node...")
finally:
    LoRa.end()