import pygame


class HID:
  def __init__(self, joystick_index=0):
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
      raise RuntimeError("No joysticks detected!")

    self.joystick_index = joystick_index
    self.joystick = pygame.joystick.Joystick(joystick_index)
    self.joystick.init()

    self.num_axes = self.joystick.get_numaxes()
    self.num_buttons = self.joystick.get_numbuttons()
    self.num_hats = self.joystick.get_numhats()

  def get_state(self):
    """Return a dictionary with axes, buttons, and hats"""
    pygame.event.pump()  # Process event queue

    axes = [self.joystick.get_axis(i) for i in range(self.num_axes)]
    buttons = [self.joystick.get_button(i) for i in range(self.num_buttons)]
    hats = [self.joystick.get_hat(i) for i in range(self.num_hats)]

    return {
      "axes": axes,
      "buttons": buttons,
      "hats": hats
    }

  def close(self):
    self.joystick.quit()
    pygame.quit()
