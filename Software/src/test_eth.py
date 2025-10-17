import socket
import argparse
import json
import time

TEENSY_IP = "10.0.0.2"
PORT = 23

millis = lambda: int(round(time.time() * 1000))

def main():
    parser = argparse.ArgumentParser(description="Teensy Ethernet communication tester")
    parser.add_argument('-s', '--send', action='store_true',
                        help='Send a test packet repeatedly (50 ms period) with alternating bit in data[0]')
    parser.add_argument('-b', '--both', action='store_true',
                        help='Receive and send test packets')
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((TEENSY_IP, PORT))
            print(f"Connected to {TEENSY_IP}:{PORT}")

            if args.both:
                buffer = ""
                msb = 0
                last_toggle_time = millis()
                while True:
                    # RX
                    s.sendall(b" ")
                    chunk = s.recv(128).decode()
                    buffer += chunk

                    while '\r\n' in buffer:
                        data, buffer = buffer.split('\r\n', 1)

                        if not data:
                            continue

                        print(data)

                    # TX
                    current_time = millis()
                    if current_time - last_toggle_time >= 2000:
                        msb ^= 1
                        last_toggle_time = current_time

                    packet = {
                        "id": 440,
                        "dlc": 8,
                        "data": [msb] + [0] * 7
                    }
                    time.sleep(50 / 1000)  # Sleep for 50 ms
                    print(f"Sending packet: {json.dumps(packet, separators=(',', ':'))}")
                    s.sendall((json.dumps(packet, separators=(',', ':')) + '\n').encode())

            if args.send:
                msb = 0
                last_toggle_time = millis()
                while True:
                    current_time = millis()
                    if current_time - last_toggle_time >= 2000:
                        msb ^= 1
                        last_toggle_time = current_time

                    packet = {
                        "id": 440,
                        "dlc": 8,
                        "data": [msb] + [0] * 7
                    }
                    time.sleep(50 / 1000)  # Sleep for 50 ms
                    print(f"Sending packet: {json.dumps(packet, separators=(',', ':'))}")
                    s.sendall((json.dumps(packet, separators=(',', ':')) + '\n').encode())

            else:
                s.sendall(b" ")
                buffer = ""
                while True:
                    chunk = s.recv(128).decode()
                    buffer += chunk

                    while '\r\n' in buffer:
                        data, buffer = buffer.split('\r\n', 1)

                        if not data:
                            continue

                        received_msg_id = json.loads(data).get("id")
                        if received_msg_id == 47 and received_msg_id == 26:
                            print(data)


        except TimeoutError:
            print(f"Connection to {TEENSY_IP}:{PORT} timed out")

        except KeyboardInterrupt:
            print("\nExited successfully")

if __name__ == "__main__":
    main()
