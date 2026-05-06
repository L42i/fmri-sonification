#!/usr/bin/env python3
"""
Logitech G / Saitek Pro Flight Yoke + Throttle + Rudder reader
+ 3D Navigation Visualizer
Requires:
    pip install pygame
"""

import sys
import math
import pygame

# ── Axis labels ────────────────────────────────────────────────────────────
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

BUTTON_LABELS = {
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
def classify(name):
    nl = name.lower()

    if "yoke" in nl or "flight yoke" in nl:
        return "yoke"

    if "throttle" in nl or "tq" in nl:
        return "throttle"

    if "rudder" in nl or "pedal" in nl:
        return "rudder"

    return "unknown"


def axis_label(kind, idx):
    labels = AXIS_LABELS.get(kind, [])
    return labels[idx] if idx < len(labels) else f"Axis {idx}"


def button_label(kind, idx):
    labels = BUTTON_LABELS.get(kind, [])
    return labels[idx] if idx < len(labels) else f"Button {idx}"


def bar(value, width=20):
    filled = int((value + 1) / 2 * width)
    filled = max(0, min(width, filled))
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def fmt_axis(v):
    return f"{v:+.4f}"


def get_axis_value_by_label(joysticks, target_labels):
    target_labels = [t.lower() for t in target_labels]

    for js in joysticks:
        kind = classify(js.get_name())

        for a in range(js.get_numaxes()):
            lbl = axis_label(kind, a).lower()

            if lbl in target_labels:
                return js.get_axis(a)

    return 0.0


def map_axis_to_0_100(value):
    return ((value + 1.0) / 2.0) * 100.0


def clamp(v, low=0.0, high=100.0):
    return max(low, min(high, v))


def project_3d(x, y, z, screen_w, screen_h):
    center_x = screen_w // 2
    center_y = screen_h // 2 + 80

    scale = 5.0
    depth = 1.0 + (z / 180.0)

    px = center_x + ((x - 50) * scale) / depth
    py = center_y - ((y - 50) * scale) / depth - ((z - 50) * 1.7)

    return int(px), int(py)


# ── Original reader ────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()

    if count == 0:
        print("No joystick/HID devices found.")
        sys.exit(1)

    joysticks = []

    for i in range(count):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

        kind = classify(js.get_name())

        print(
            f"[{i}] {js.get_name()} → kind={kind} "
            f"axes={js.get_numaxes()} "
            f"buttons={js.get_numbuttons()} "
            f"hats={js.get_numhats()}"
        )

    print("\nReading controls — press Ctrl-C to quit.\n")
    print("─" * 72)

    clock = pygame.time.Clock()

    try:
        while True:
            pygame.event.pump()

            lines = []

            for js in joysticks:
                name = js.get_name()
                kind = classify(name)

                lines.append(f"\n▶ {name} ({kind})")

                for a in range(js.get_numaxes()):
                    v = js.get_axis(a)
                    lbl = axis_label(kind, a)
                    lines.append(
                        f"  {lbl:<30} {fmt_axis(v)}  {bar(v)}"
                    )

                pressed = [
                    button_label(kind, b)
                    for b in range(js.get_numbuttons())
                    if js.get_button(b)
                ]

                if pressed:
                    lines.append(
                        f"  BUTTONS HELD: {', '.join(pressed)}"
                    )
                else:
                    lines.append("  BUTTONS HELD: (none)")

            output = "\n".join(lines)
            num_lines = output.count("\n") + 1

            print(output, end="", flush=True)
            print(f"\x1b[{num_lines}A", end="", flush=True)

            clock.tick(20)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        for js in joysticks:
            js.quit()

        pygame.quit()


# ── 3D Visualizer ──────────────────────────────────────────────────────────
def run_visualizer():
    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()

    if count == 0:
        print("No joystick found.")
        return

    joysticks = []

    for i in range(count):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

    screen_w = 1300
    screen_h = 850

    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("3D Brain Navigation")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    small = pygame.font.SysFont("Arial", 16)

    trail = []

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.event.pump()

        # axes
        roll = get_axis_value_by_label(joysticks, ["aileron (roll)"])
        pitch = get_axis_value_by_label(joysticks, ["elevator (pitch)"])
        throttle1 = get_axis_value_by_label(joysticks, ["throttle 1"])
        throttle2 = get_axis_value_by_label(joysticks, ["throttle 2"])

        # map
        x = clamp(map_axis_to_0_100(roll))
        y = clamp(map_axis_to_0_100(pitch))
        z = clamp(map_axis_to_0_100(throttle1))
        t = clamp(map_axis_to_0_100(throttle2))

        px, py = project_3d(x, y, z, screen_w, screen_h)

        trail.append((px, py))
        if len(trail) > 600:
            trail.pop(0)

        screen.fill((7, 10, 20))

        # 3D cube layers
        for level in range(0, 101, 25):
            pts = [
                project_3d(0, 0, level, screen_w, screen_h),
                project_3d(100, 0, level, screen_w, screen_h),
                project_3d(100, 100, level, screen_w, screen_h),
                project_3d(0, 100, level, screen_w, screen_h),
            ]

            pygame.draw.lines(screen, (40, 50, 80), True, pts, 1)

        # axis lines
        pygame.draw.line(
            screen,
            (220, 80, 80),
            project_3d(0, 50, 50, screen_w, screen_h),
            project_3d(100, 50, 50, screen_w, screen_h),
            2
        )

        pygame.draw.line(
            screen,
            (80, 220, 120),
            project_3d(50, 0, 50, screen_w, screen_h),
            project_3d(50, 100, 50, screen_w, screen_h),
            2
        )

        pygame.draw.line(
            screen,
            (80, 130, 255),
            project_3d(50, 50, 0, screen_w, screen_h),
            project_3d(50, 50, 100, screen_w, screen_h),
            2
        )

        # trail
        if len(trail) > 1:
            pygame.draw.lines(
                screen,
                (100, 180, 255),
                False,
                trail,
                2
            )

        # point
        pygame.draw.circle(screen, (255, 100, 100), (px, py), 14)
        pygame.draw.circle(screen, (255, 255, 255), (px, py), 20, 2)

        # time bar
        pygame.draw.rect(screen, (45, 45, 70), (80, 760, 900, 26))
        pygame.draw.rect(
            screen,
            (255, 220, 100),
            (80, 760, int(900 * t / 100), 26)
        )

        # HUD
        panel = pygame.Rect(980, 50, 260, 260)
        pygame.draw.rect(screen, (20, 25, 45), panel)
        pygame.draw.rect(screen, (100, 120, 170), panel, 2)

        lines = [
            "3D Navigation",
            "",
            f"Roll X       {x:6.2f}",
            f"Pitch Y      {y:6.2f}",
            f"Throttle1 Z  {z:6.2f}",
            f"Throttle2 T  {t:6.2f}",
            "",
            "Range: 0-100",
            "Center: 50",
        ]

        yy = 70
        for line in lines:
            surf = font.render(line, True, (240, 240, 240))
            screen.blit(surf, (1000, yy))
            yy += 28

        labels = [
            "Roll → Left / Right",
            "Pitch → Forward / Back",
            "Throttle1 → Up / Down",
            "Throttle2 → Time",
        ]

        yy = 40
        for line in labels:
            surf = small.render(line, True, (210, 220, 255))
            screen.blit(surf, (60, yy))
            yy += 20

        pygame.display.flip()
        clock.tick(60)

    for js in joysticks:
        js.quit()

    pygame.quit()


# ── Entry ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mode = "visual"   # "reader" or "visual"

    if mode == "reader":
        main()
    else:
        run_visualizer()