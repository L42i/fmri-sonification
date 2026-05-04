global int N;
global float current[N][6];

-4.298912525177 => float magicMin;
6.28821420669556 => float magicMax;

LiSa lisas[N];

for (int i; i < N; i++) {
  lisas[i] => (i => dac.chan);

  8 => lisas[i].maxVoices;

  spork ~ grains(i);
}

"/Users/tristanpeng/Documents/CS/Projects/fmri-sonification/samples/3/e/mid/supported.wav" => read;

fun void read(string name) {
  for (int i; i < N; i++) name => lisas[i].read;
}

fun void grain(int i) {
  lisas[i] @=> LiSa @ lisa;

  lisa.getVoice() => int voice;

  if (voice > -1) {
    (current[i][1], magicMin, magicMax, 0.5, 1.5) => Math.map => float rate;
    (current[i][2], 0, 1, 0, lisa.duration() / samp) => Math.map => float pos;
    current[i][3]::ms => dur len;
    current[i][4]::ms => dur up;
    current[i][5]::ms => dur down;

    (voice, rate) => lisa.rate;
    (voice, pos::samp) => lisa.playPos;
    (voice, up) => lisa.rampUp;

    (len - up) => now;

    (voice, down) => lisa.rampDown;

    down => now;
  }
}

fun void grains(int i) {
  while (true) {
    if (current[i][0]) spork ~ grain(i);
    (current[i][1], magicMin, magicMax, 20, 90) => Math.map => float wait;
    wait::ms => now;
  }
}

eon => now;