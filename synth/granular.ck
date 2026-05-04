global int N;
global float current[N][2];

// magic numbers
-4.298912525177 => float magicMin;
6.28821420669556 => float magicMax;

LiSa lisas[N];
Gain gains[N];

for (int i; i < N; i++) {
  lisas[i] => gains[i] => (i => dac.chan);

  8 => lisas[i].maxVoices;
  0.02 => gains[i].gain;

  spork ~ grains(i);
}

for (int i; i < N; i++) me.dir() + "../samples/hc" + i + ".wav" => lisas[i].read;

fun void grain(int i) {
  lisas[i] @=> LiSa @ lisa;

  lisa.getVoice() => int voice;

  if (voice > -1) {
    (current[i][1], magicMin, magicMax, 0.5, 1.5) => Math.map => float rate;
    (0, lisa.duration() / samp) => Math.random2f => float pos;
    100::ms => dur len;
    5::ms => dur up;
    5::ms => dur down;

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