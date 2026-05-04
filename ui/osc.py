from pythonosc.udp_client import SimpleUDPClient

class OSC:
  def __init__(self, port=6667):
    self.client = SimpleUDPClient('127.0.0.1', port)

  def send(self, address, message):
    assert len(address) > 1 and address[0] == '/'
    assert message is not None
    self.client.send_message(address, message)