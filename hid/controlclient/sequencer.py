import time
import os
from pythonosc import udp_client
from PyQt5.QtCore import QThread, pyqtSignal
import pygame

# the axis-label reading approach from yoke.py
AXIS_LABELS = {
    "yoke": [
        "Aileron (Roll)",
        "Elevator (Pitch)",
        "Throttle 1",
        "Throttle 2",
        "Prop Pitch / Mixture",
        "Toe Brake L",
        "Toe Brake R",
    ],
    "throttle": [
        "Throttle 1",
        "Throttle 2",
        "Prop Pitch",
        "Mixture",
        "Carb Heat / Spare",
    ],
    "rudder": [
        "Rudder",
        "Toe Brake L",
        "Toe Brake R",
    ],
}

def classify(name: str) -> str:
    nl = name.lower()
    if "yoke" in nl or "flight yoke" in nl:
        return "yoke"
    if "throttle" in nl or "tq" in nl:
        return "throttle"
    if "rudder" in nl or "pedal" in nl:
        return "rudder"
    return "unknown"

def axis_label(kind: str, idx: int) -> str:
    labels = AXIS_LABELS.get(kind, [])
    return labels[idx] if idx < len(labels) else f"Axis {idx}"

def get_axis_value_by_label(joysticks, target_labels):
    target_labels = [label.lower() for label in target_labels]

    for js in joysticks:
        kind = classify(js.get_name())
        for axis_index in range(js.get_numaxes()):
            label = axis_label(kind, axis_index).lower()
            if label in target_labels:
                return js.get_axis(axis_index)
    return 0.0



class SequencerThread(QThread):
    status = pyqtSignal(str)

    # default variable initializing (don't touch most of this, except deadzones and thresholds)
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.is_paused = False
        self.is_stopped = False
        self.ip = "127.0.0.1" # default ip
        self.port = 1337 # default port
        self.client = None
        self.axis_deadzone = 0.10 
        self.change_threshold = 0.01

    def run(self):

        # pygame intialization (DO NOT touch this)
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.display.init()
        pygame.display.set_mode((1, 1))
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            joystick.init()

        try:
            if pygame.joystick.get_count() == 0:
                self.status.emit("Error: no joystick found")
                return

            # debugging stuff; displays basic info about joysticks
            for idx, js in enumerate(joysticks):
                self.status.emit(
                    f"Joystick[{idx}] {js.get_name()} | kind={classify(js.get_name())} | axes={js.get_numaxes()} buttons={js.get_numbuttons()}"
                )

            prev_roll = None
            prev_elevator = None
            while not self.is_stopped:
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.05)

                if self.is_stopped:
                    self.status.emit("Stopped")
                    return

                pygame.event.pump() # refreshes axis values (don't touch)

                # the actual values (goes from -1 to 1)
                roll = get_axis_value_by_label(joysticks, ["aileron (roll)"])
                elevator = get_axis_value_by_label(joysticks, ["elevator (pitch)"])

                # deadzoning controls
                if abs(roll) < self.axis_deadzone:
                    roll = 0.0
                if abs(elevator) < self.axis_deadzone:
                    elevator = 0.0

                # core of osc message sending (for now just roll and elevator)
                if prev_roll is None or abs(roll - prev_roll) >= self.change_threshold:
                    self.client.send_message("/controller/roll", roll) # sends the osc messages -> sends the value (as a float), at address "/controller/roll"
                    prev_roll = roll
                    self.status.emit(f"Sent /controller/roll: {roll:+.4f}, IP: {self.ip}, Port: {self.port}") # this is just for the log or "terminal", not the actual osc message

                if prev_elevator is None or abs(elevator - prev_elevator) >= self.change_threshold:
                    self.client.send_message("/controller/elevator", elevator) # sends the osc messages -> sends the value (as a float), at address "/controller/elevator"
                    prev_elevator = elevator
                    self.status.emit(f"Sent /controller/elevator: {elevator:+.4f}, IP: {self.ip}, Port: {self.port}") # this is just for the log or "terminal", not the actual osc message

                time.sleep(0.05) 

        except Exception as e:
            self.status.emit(f"Error: {e}")
        finally:
            for joystick in joysticks:
                joystick.quit()
            pygame.joystick.quit()
            pygame.display.quit()


    # helper methods
    def pause(self):
        self.is_paused = True
        self.status.emit("Paused")

    def resume(self):
        self.is_paused = False
        self.status.emit("Playing")

    def stop(self):
        self.is_stopped = True
        self.is_paused = False

    def set_port(self, port):
        self.port = port
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)

    def set_ip(self, ip):
        self.ip = ip
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
