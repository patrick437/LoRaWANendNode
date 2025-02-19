from RadioLib import SX1262
import time
import struct

# LoRaWAN credentials from AWS IoT Core
DEVEUI = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Replace with yours
APPEUI = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Replace with yours
APPKEY = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Replace with yours
         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

# Pin definitions for Raspberry Pi
NSS_PIN = 10    # GPIO 10 - SPI CS
RESET_PIN = 18  # GPIO 18
BUSY_PIN = 20   # GPIO 20
IRQ_PIN = 16    # GPIO 16
DIO1_PIN = 16   # Same as IRQ

# Initialize SX1262
radio = SX1262(NSS_PIN, RESET_PIN, BUSY_PIN, IRQ_PIN)

def setup_lorawan():
    print("Initializing LoRaWAN...")
    
    # Initialize radio
    state = radio.begin()
    if state != radio.ERR_NONE:
        raise Exception(f"Failed to initialize radio: {state}")
    
    # Set LoRaWAN parameters
    print("Setting up LoRaWAN parameters...")
    radio.setFrequency(868100000)  # EU868 frequency
    radio.setBandwidth(125.0)      # 125 kHz bandwidth
    radio.setSpreadingFactor(7)    # SF7
    radio.setCodingRate(5)         # 4/5 coding rate
    radio.setOutputPower(14)       # 14 dBm output power
    radio.setPreambleLength(8)     # Standard LoRaWAN preamble length
    
    # Set LoRaWAN credentials
    print("Setting LoRaWAN credentials...")
    radio.setDeviceEUI(DEVEUI)
    radio.setApplicationEUI(APPEUI)
    radio.setApplicationKey(APPKEY)

def join_network():
    print("Attempting to join LoRaWAN network...")
    
    join_attempts = 0
    max_attempts = 5
    
    while join_attempts < max_attempts:
        state = radio.joinOTAA()
        if state == radio.ERR_NONE:
            print("Successfully joined the network!")
            return True
        
        join_attempts += 1
        print(f"Join failed (attempt {join_attempts}/{max_attempts})")
        time.sleep(5)
    
    return False

def send_data(payload):
    print("Preparing to send data...")
    
    # Send unconfirmed uplink on port 1
    state = radio.beginPacket(1)
    if state != radio.ERR_NONE:
        print(f"Failed to start packet: {state}")
        return False
    
    # Write payload
    radio.write(payload)
    
    # Send packet
    state = radio.endPacket()
    if state == radio.ERR_NONE:
        print("Packet sent successfully!")
        return True
    else:
        print(f"Failed to send packet: {state}")
        return False

def main():
    try:
        # Setup LoRaWAN
        setup_lorawan()
        
        # Join network
        if not join_network():
            raise Exception("Failed to join network after maximum attempts")
        
        # Main loop
        counter = 0
        while True:
            # Create sample payload (replace with your sensor data)
            temperature = 23.5
            humidity = 65.0
            payload = struct.pack('ff', temperature, humidity)
            
            # Send data
            if send_data(payload):
                print(f"Message {counter} sent successfully")
                print(f"Temperature: {temperature}°C")
                print(f"Humidity: {humidity}%")
            else:
                print(f"Failed to send message {counter}")
            
            counter += 1
            
            # Wait before next transmission (respect duty cycle)
            time.sleep(300)  # 5 minutes
    
    except KeyboardInterrupt:
        print("\nStopping LoRaWAN node...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        radio.sleep()

if __name__ == "__main__":
    main()