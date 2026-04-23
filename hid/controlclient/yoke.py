#!/usr/bin/env python3
"""
Logitech G / Saitek Pro Flight Yoke + Throttle + Rudder reader
Requires: pip install pygame
On Linux the bundle exposes 2-3 separate joystick devices; this script
reads all of them simultaneously and prints live control values.
"""

import sys
import pygame

# ── Axis labels per device name (partial-match, case-insensitive) ──────────
# Extend / adjust these if your kernel assigns different names.
AXIS_LABELS: dict[str, list[str]] = {
    "yoke": [
        "Aileron (Roll)",       # axis 0
        "Elevator (Pitch)",     # axis 1
        "Throttle 1",           # axis 2
        "Throttle 2",           # axis 3
        "Prop Pitch / Mixture", # axis 4
        "Toe Brake L",          # axis 5
        "Toe Brake R",          # axis 6
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

BUTTON_LABELS: dict[str, list[str]] = {
    "yoke": [
        "B1 (Trigger)",
        "B2", "B3", "B4",
        "B5 (Hat Switch A Up)",
        "B6 (Hat Switch A Dn)",
        "B7 (Hat Switch A L)",
        "B8 (Hat Switch A R)",
        "B9", "B10", "B11", "B12",
        "B13 (Autopilot Disc)",
        "B14 (TOGA)",
    ],
    "throttle": [
        "B1", "B2", "B3", "B4",
        "B5 (Flap Up)",
        "B6 (Flap Dn)",
        "B7 (Gear Up)",
        "B8 (Gear Dn)",
    ],
    "rudder": [],
}


# ── Helpers ────────────────────────────────────────────────────────────────

def classify(name: str) -> str:
    """Return 'yoke', 'throttle', 'rudder', or 'unknown'."""
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


def button_label(kind: str, idx: int) -> str:
    labels = BUTTON_LABELS.get(kind, [])
    return labels[idx] if idx < len(labels) else f"Button {idx}"


def bar(value: float, width: int = 20) -> str:
    """ASCII bar for an axis value in [-1, 1]."""
    filled = int((value + 1) / 2 * width)
    filled = max(0, min(width, filled))
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def fmt_axis(v: float) -> str:
    return f"{v:+.4f}"


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    if count == 0:
        print("No joystick/HID devices found.")
        print("  • Make sure the bundle is plugged in.")
        print("  • Try:  ls /dev/input/js*")
        print("  • You may need:  pip install pygame")
        sys.exit(1)

    joysticks: list[pygame.joystick.JoystickType] = []
    for i in range(count):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)
        kind = classify(js.get_name())
        print(
            f"  [{i}] {js.get_name()!r}  →  kind={kind}  "
            f"axes={js.get_numaxes()}  buttons={js.get_numbuttons()}  "
            f"hats={js.get_numhats()}"
        )

    print("\nReading controls — press Ctrl-C to quit.\n")
    print("─" * 72)

    clock = pygame.time.Clock()

    try:
        while True:
            pygame.event.pump()   # pull OS events so values update

            lines: list[str] = []
            for js in joysticks:
                name = js.get_name()
                kind = classify(name)
                lines.append(f"\n▶ {name} ({kind})")

                # Axes
                for a in range(js.get_numaxes()):
                    v = js.get_axis(a)
                    lbl = axis_label(kind, a)
                    lines.append(f"  {lbl:<30} {fmt_axis(v)}  {bar(v)}")

                # Buttons  (only show pressed ones to reduce noise)
                pressed = [
                    button_label(kind, b)
                    for b in range(js.get_numbuttons())
                    if js.get_button(b)
                ]
                if pressed:
                    lines.append(f"  BUTTONS HELD: {', '.join(pressed)}")
                else:
                    lines.append("  BUTTONS HELD: (none)")

                # Hats / POV switches
                for h in range(js.get_numhats()):
                    hv = js.get_hat(h)
                    directions = {
                        ( 0,  0): "Centered",
                        ( 0,  1): "Up",
                        ( 0, -1): "Down",
                        (-1,  0): "Left",
                        ( 1,  0): "Right",
                        ( 1,  1): "Up-Right",
                        (-1,  1): "Up-Left",
                        ( 1, -1): "Down-Right",
                        (-1, -1): "Down-Left",
                    }
                    lines.append(
                        f"  Hat {h}: {hv}  →  {directions.get(hv, str(hv))}"
                    )

            # Overwrite in place
            output = "\n".join(lines)
            num_lines = output.count("\n") + 1
            print(output, end="", flush=True)
            # Move cursor back up
            print(f"\x1b[{num_lines}A", end="", flush=True)

            clock.tick(20)   # 20 Hz refresh

    except KeyboardInterrupt:
        print("\n\nStopped.")
    finally:
        for js in joysticks:
            js.quit()
        pygame.quit()

# ── Visual Section ──────────────────────────────────────────────────────────
# Add this BELOW your existing code. It does not replace the reader.

import math


def get_axis_value_by_label(joysticks, target_labels):
    """
    Search all joysticks for an axis whose label matches one of target_labels.
    Returns the first matching axis value, else 0.0.
    """
    target_labels = [t.lower() for t in target_labels]

    for js in joysticks:
        kind = classify(js.get_name())
        for a in range(js.get_numaxes()):
            lbl = axis_label(kind, a).lower()
            if lbl in target_labels:
                return js.get_axis(a)
    return 0.0


def run_visualizer():
    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    if count == 0:
        print("No joystick/HID devices found for visualizer.")
        return

    joysticks = []
    for i in range(count):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

    screen_w, screen_h = 1100, 750
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Flight Navigation Visualizer")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22)
    small_font = pygame.font.SysFont("Arial", 16)

    # Starting position
    x = screen_w // 2
    y = screen_h // 2

    # Trail of visited points
    trail = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.event.pump()

        # Read main controls from your existing joystick labeling system
        roll = get_axis_value_by_label(joysticks, ["aileron (roll)"])
        pitch = get_axis_value_by_label(joysticks, ["elevator (pitch)"])
        rudder = get_axis_value_by_label(joysticks, ["rudder"])
        throttle = get_axis_value_by_label(
            joysticks,
            ["throttle 1", "throttle 2"]
        )

        # Deadzones
        if abs(roll) < 0.05:
            roll = 0.0
        if abs(pitch) < 0.05:
            pitch = 0.0
        if abs(rudder) < 0.05:
            rudder = 0.0
        if abs(throttle) < 0.05:
            throttle = 0.0

        # Convert throttle to movement speed
        # Many throttles rest around -1 to +1, so normalize to 0..1
        speed_factor = (throttle + 1) / 2.0
        speed = 2 + speed_factor * 10

        # Move visual marker
        x += roll * speed * 2.5
        y += pitch * speed * 2.5

        # Rudder adds slight horizontal bias
        x += rudder * speed * 1.2

        # Clamp to screen
        x = max(40, min(screen_w - 40, x))
        y = max(40, min(screen_h - 40, y))

        # Save trail
        trail.append((int(x), int(y)))
        if len(trail) > 800:
            trail.pop(0)

        # Draw
        screen.fill((8, 10, 18))

        # Grid
        grid_spacing = 50
        for gx in range(0, screen_w, grid_spacing):
            pygame.draw.line(screen, (30, 38, 60), (gx, 0), (gx, screen_h), 1)
        for gy in range(0, screen_h, grid_spacing):
            pygame.draw.line(screen, (30, 38, 60), (0, gy), (screen_w, gy), 1)

        # Center crosshair
        pygame.draw.line(screen, (70, 90, 130), (screen_w // 2, 0), (screen_w // 2, screen_h), 1)
        pygame.draw.line(screen, (70, 90, 130), (0, screen_h // 2), (screen_w, screen_h // 2), 1)

        # Draw trail
        if len(trail) > 1:
            pygame.draw.lines(screen, (100, 180, 255), False, trail, 2)

        # Marker size reacts to throttle
        marker_radius = int(10 + speed_factor * 18)

        # Glow
        pygame.draw.circle(screen, (60, 120, 255), (int(x), int(y)), marker_radius + 12, 2)
        pygame.draw.circle(screen, (255, 100, 100), (int(x), int(y)), marker_radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), marker_radius + 4, 2)

        # Heading line based on roll + pitch
        angle = math.atan2(pitch, roll if roll != 0 else 0.0001)
        line_len = 45
        hx = int(x + math.cos(angle) * line_len)
        hy = int(y + math.sin(angle) * line_len)
        pygame.draw.line(screen, (255, 230, 120), (int(x), int(y)), (hx, hy), 3)

        # HUD panel
        panel = pygame.Rect(800, 30, 270, 220)
        pygame.draw.rect(screen, (20, 25, 40), panel, border_radius=12)
        pygame.draw.rect(screen, (90, 110, 150), panel, 2, border_radius=12)

        lines = [
            "Navigation Visual",
            f"Roll:      {roll:+.3f}",
            f"Pitch:     {pitch:+.3f}",
            f"Rudder:    {rudder:+.3f}",
            f"Throttle:  {throttle:+.3f}",
            f"Speed:     {speed:.2f}",
            f"X:         {x:.1f}",
            f"Y:         {y:.1f}",
        ]

        ty = 45
        for i, text in enumerate(lines):
            surf = font.render(text, True, (235, 235, 235))
            screen.blit(surf, (820, ty))
            ty += 26

        # Device list
        device_title = small_font.render("Connected devices:", True, (180, 200, 255))
        screen.blit(device_title, (30, 20))

        dy = 45
        for i, js in enumerate(joysticks):
            info = f"[{i}] {js.get_name()}"
            surf = small_font.render(info, True, (180, 180, 180))
            screen.blit(surf, (30, dy))
            dy += 18

        # Instructions
        info_lines = [
            "Controls:",
            "Roll = left / right",
            "Pitch = up / down",
            "Rudder = side bias",
            "Throttle = speed / marker size",
            "Close window to quit"
        ]
        iy = 280
        for text in info_lines:
            surf = small_font.render(text, True, (220, 220, 220))
            screen.blit(surf, (820, iy))
            iy += 22

        pygame.display.flip()
        clock.tick(60)

    for js in joysticks:
        js.quit()
    pygame.quit()

if __name__ == "__main__":
    mode = "visual"   # change to "reader" if needed

    if mode == "reader":
        main()
    elif mode == "visual":
        run_visualizer()