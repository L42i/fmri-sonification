import time
import csv
import os
from pythonosc import udp_client
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
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

    # default variable initializing (don't touch most of this)
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.is_paused = False
        self.is_stopped = False
        self.ip = "127.0.0.1" # default ip
        self.port = 1337 # default port
        self.row = 0
        self.client = None
        self.axis_scale = 5.0 # adjusts the sliding window scaling
        self.axis_deadzone = 0.10

    def run(self):

        # pygame intialization
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

            # debugging stuff; displays info about joysticks
            for idx, js in enumerate(joysticks):
                self.status.emit(
                    f"Joystick[{idx}] {js.get_name()} | kind={classify(js.get_name())} | axes={js.get_numaxes()} buttons={js.get_numbuttons()}"
                )

            column_ranges = self.get_column_ranges()
            if not column_ranges:
                self.status.emit("Error: no numeric data found in file")
                return

            # row sequencing portion; goes through each cell, normalizes the value based on min/max (0 to 1), and adds (appends) it to the normalized_row list 
            normalized_rows = []
            with open(self.filepath, newline="") as f:
                for row in csv.reader(f):
                    normalized_row = []
                    for idx, cell in enumerate(row):
                        try:
                            value = float(cell)
                        except ValueError:
                            continue

                        data_min, data_max = column_ranges.get(idx, (None, None))
                        if data_min is None or data_max is None:
                            continue

                        normalized_row.append(self.normalize_minmax(value, data_min, data_max))

                    if normalized_row:
                        normalized_rows.append(normalized_row)

            if not normalized_rows:
                self.status.emit("Error: no numeric rows found in file")
                return


            # osc message sending portion
            prevRow = None
            while not self.is_stopped:
                while self.is_paused and not self.is_stopped:
                    time.sleep(0.05)

                if self.is_stopped:
                    self.status.emit("Stopped")
                    return

                # core of the osc message sending
                index = int(np.clip(self.row, 0, len(normalized_rows) - 1))
                if index != prevRow: # only sends if the row (index) currently isn't the same as before
                    self.client.send_message("/row", normalized_rows[index]) # this is what sends the osc messages; sends a List with the values at address "/row"
                    prevRow = index
                    self.status.emit(
                        f"Sent row: {index}, IP: {self.ip}, Port: {self.port}" # this is just for the log or "terminal", not the actual osc message
                    )

                pygame.event.pump() # refreshes the joystick values (don't touch)
                axis_value = get_axis_value_by_label(joysticks, ["elevator (pitch)"]) # the actual value we're getting from the joystick

                # deadzoning control; adjust with self.axis_deadzone variable near the top
                if abs(axis_value) < self.axis_deadzone:
                    axis_value = 0.0

                # the actual "sliding window" line; exponential scaling, adjust it with the self.axis_scale variable near the top
                self.row += (-axis_value ** 3) * self.axis_scale

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

    def set_row(self, row):
        self.row = row

    def get_column_ranges(self):
        column_values = {}
        with open(self.filepath, newline="") as f:
            for row in csv.reader(f):
                for idx, cell in enumerate(row):
                    try:
                        value = float(cell)
                    except ValueError:
                        continue
                    column_values.setdefault(idx, []).append(value)

        ranges = {}
        for idx, values in column_values.items():
            if values:
                ranges[idx] = (min(values), max(values))
        return ranges

    def normalize_minmax(self, value, data_min, data_max):
        if data_max == data_min:
            return 0
        return (value - data_min) / (data_max - data_min)
