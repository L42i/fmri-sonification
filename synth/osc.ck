global int N;
global float current[N][2];

OscIn oin;

6667 => oin.port;

cherr <= "listening for OSC messages over port: " <= oin.port()
      <= "..." <= IO.newline();

oin.listenAll();

OscMsg msg;

while (true) {
  oin => now;

  while (msg => oin.recv) {
    if (msg.address != "/row") continue;

    (msg.numArgs(), N) => Math.min => int end;
    for (int n; n < end; n++) {
      true => current[n][0]; // playing
      n => msg.getFloat => current[n][1]; // row
    }
  }
}