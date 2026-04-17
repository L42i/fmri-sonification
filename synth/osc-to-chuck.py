from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

LISTEN_IP = "10.10.10.25"
LISTEN_PORT = 6667

REAPER_IP = "127.0.0.1"
REAPER_PORT = 8000

INPUT_DATA_ADDRESS = "/row"
INPUT_YOKE_ADDRESS = "/controller/yoke"
INPUT_ROLL_ADDRESS = "/controller/roll"
INPUT_THROTTLE1_ADDRESS = "/controller/throttle1"
INPUT_THROTTLE2_ADDRESS = "/controller/throttle2"
INPUT_THROTTLE3_ADDRESS = "/controller/throttle3"

EXPECTED_COUNT = 53

client = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)


def send_53_channels(values):
    client.send_message("/controller1", values[0]) 
    client.send_message("/controller2", values[1]) 
    client.send_message("/controller3", values[2]) 
    client.send_message("/controller4", values[3]) 
    client.send_message("/controller5", values[4]) 
    client.send_message("/controller6", values[5]) 
    client.send_message("/controller7", values[6]) 
    client.send_message("/controller8", values[7]) 
    client.send_message("/controller9", values[8]) 
    client.send_message("/controller10", values[9]) 
    client.send_message("/controller11", values[10]) 
    client.send_message("/controller12", values[11]) 
    client.send_message("/controller13", values[12]) 
    client.send_message("/controller14", values[13]) 
    client.send_message("/controller15", values[14]) 
    client.send_message("/controller16", values[15]) 
    client.send_message("/controller17", values[16]) 
    client.send_message("/controller18", values[17]) 
    client.send_message("/controller19", values[18]) 
    client.send_message("/controller20", values[19]) 
    client.send_message("/controller21", values[20]) 
    client.send_message("/controller22", values[21]) 
    client.send_message("/controller23", values[22]) 
    client.send_message("/controller24", values[23]) 
    client.send_message("/controller25", values[24]) 
    client.send_message("/controller26", values[25]) 
    client.send_message("/controller27", values[26]) 
    client.send_message("/controller28", values[27]) 
    client.send_message("/controller29", values[28]) 
    client.send_message("/controller30", values[29]) 
    client.send_message("/controller31", values[30]) 
    client.send_message("/controller32", values[31]) 
    client.send_message("/controller33", values[32]) 
    client.send_message("/controller34", values[33]) 
    client.send_message("/controller35", values[34]) 
    client.send_message("/controller36", values[35]) 
    client.send_message("/controller37", values[36]) 
    client.send_message("/controller38", values[37]) 
    client.send_message("/controller39", values[38]) 
    client.send_message("/controller40", values[39]) 
    client.send_message("/controller41", values[40]) 
    client.send_message("/controller42", values[41]) 
    client.send_message("/controller43", values[42]) 
    client.send_message("/controller44", values[43]) 
    client.send_message("/controller45", values[44]) 
    client.send_message("/controller46", values[45]) 
    client.send_message("/controller47", values[46]) 
    client.send_message("/controller48", values[47]) 
    client.send_message("/controller49", values[48]) 
    client.send_message("/controller50", values[49]) 
    client.send_message("/controller51", values[50]) 
    client.send_message("/controller52", values[51]) 
    client.send_message("/controller0", values[52])

def handle_data(address, *args):
    print(f"\nReceived DATA: {address}, count={len(args)}")

    if len(args) != EXPECTED_COUNT:
        print(f"[WARNING] Expected {EXPECTED_COUNT}, got {len(args)}")
        return

    values = []
    for i, arg in enumerate(args):
        try:
            values.append(float(arg))
        except ValueError:
            print(f"[ERROR] Non-numeric value at index {i}")
            return

    send_53_channels(values)
    print("sending to ChucK")


def handle_yoke(address, *args):
    print(f"\nReceived YOKE: {address}, args={args}")
    if len(args) < 1:
        return

    value = float(args[0])
    client.send_message("/controller/yoke", value)


def handle_roll(address, *args):
    print(f"\nReceived ROLL: {address}, args={args}")
    if len(args) < 1:
        return

    value = float(args[0])
    client.send_message("/controller/roll", value)


def handle_throttle1(address, *args):
    print(f"\nReceived THROTTLE1: {address}, args={args}")
    if len(args) < 1:
        return

    value = float(args[0])
    client.send_message("/controller/throttle1", value)


def handle_throttle2(address, *args):
    print(f"\nReceived THROTTLE2: {address}, args={args}")
    if len(args) < 1:
        return

    value = float(args[0])
    client.send_message("/controller/throttle2", value)


def handle_throttle3(address, *args):
    print(f"\nReceived THROTTLE3: {address}, args={args}")
    if len(args) < 1:
        return

    value = float(args[0])
    client.send_message("/controller/throttle3", value)


def main():
    disp = dispatcher.Dispatcher()

    disp.map(INPUT_DATA_ADDRESS, handle_data)
    disp.map(INPUT_YOKE_ADDRESS, handle_yoke)
    disp.map(INPUT_ROLL_ADDRESS, handle_roll)
    disp.map(INPUT_THROTTLE1_ADDRESS, handle_throttle1)
    disp.map(INPUT_THROTTLE2_ADDRESS, handle_throttle2)
    disp.map(INPUT_THROTTLE3_ADDRESS, handle_throttle3)

    print("=== OSC REAPER Bridge ===")
    print(f"Listening: {LISTEN_IP}:{LISTEN_PORT}")
    print(f"Forwarding to REAPER: {REAPER_IP}:{REAPER_PORT}")

    server = osc_server.ThreadingOSCUDPServer((LISTEN_IP, LISTEN_PORT), disp)

    print("Server started.")
    server.serve_forever()


if __name__ == "__main__":
    main()