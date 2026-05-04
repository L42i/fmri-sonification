import time
from hid import HID
from osc import OSC
from loader import Data

stick = HID()
chuck = OSC()
icst = OSC(port=6668)
data = Data()

data.read_csv_files()

# axes: [left/right, forwards/backwards, up/down, <unused>, time]

d = data.get_data('timecourses_hc.csv')

scale = lambda x, x1, y1, x2, y2: x2 + (x - x1) * (y2 - x2) / (y1 - x1)

pos = [0, 0, 0]

try:
  while True:
    state = stick.get_state()

    # update pos
    pos[0] += state['axes'][0] * 0.02
    pos[0] = max(-1, min(1, pos[0]))
    pos[1] += state['axes'][1] * 0.02
    pos[1] = max(-1, min(1, pos[1]))
    pos[2] = max(-1, min(1, -state['axes'][2]))

    # pos => ICST
    icst.send('/icst/ambi/group/xyz', ['Brain', pos[0], pos[1], pos[2], 1])

    # row => ChucK
    row = scale(state['axes'][4], -1, 1, 0, len(d))
    chuck.send('/row', d[int(row)])

    time.sleep(0.05)  # 20 Hz

except KeyboardInterrupt:
  print("Exiting...")

finally:
  stick.close()
