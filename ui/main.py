import time
from hid import HID
from osc import OSC
from loader import Data

stick = HID()
chuck = OSC()
icst = OSC(port=6668)
data = Data()

data.read_csv_files()

# axes: [left/right, forwards/backwards, up/down, time, stretch]

hc = data.get_data('timecourses_hc.csv')
sz = data.get_data('timecourses_sz.csv')

scale = lambda x, x1, y1, x2, y2: x2 + (x - x1) * (y2 - x2) / (y1 - x1)

pos = [0, 0, 0]

fire = False
is_hc = True

try:
  while True:
    state = stick.get_state()

    if state['buttons'][1] == 1 and not fire:
      fire = True
      is_hc = not is_hc
    elif state['buttons'][1] == 0 and fire:
      fire = False
      chuck.send('/fire', 0)
      print('control' if is_hc else 'schizophrenia')

    # update pos
    pos[0] += state['axes'][0] * 0.06
    pos[0] = max(-1, min(1, pos[0]))
    pos[1] -= state['axes'][1] * 0.06
    pos[1] = max(-1, min(1, pos[1]))
    pos[2] = max(-1, min(1, -state['axes'][2]))

    # pos => ICST
    icst.send('/icst/ambi/group/xyz', ['Brain', pos[0], pos[1], pos[2], 1])
    icst.send('/icst/ambi/group/setstretch', ['Brain', 10 - 5 * (state['axes'][4] + 1)])

    # row => ChucK
    if is_hc:
      row = hc[int(scale(state['axes'][3], -1, 1, 0, len(hc)))]
    else:
      row = sz[int(scale(state['axes'][3], -1, 1, 0, len(sz)))]
    chuck.send('/row', row)

    time.sleep(0.05)  # 20 Hz

except KeyboardInterrupt:
  print("Exiting...")

finally:
  stick.close()
