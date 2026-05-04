global int N;
global float current[N][2];
global Event fire;

// magic numbers
-4.298912525177 => float magicMin;
6.28821420669556 => float magicMax;

LiSa lisas[N];
Gain gains[N];

for (int i; i < N; i++) {
  lisas[i] => gains[i] => (i => dac.chan);

  1 => lisas[i].loop;
  1 => lisas[i].bi;
  8 => lisas[i].maxVoices;

  spork ~ grains(i);
}

//for (int i; i < N; i++) me.dir() + "../samples/supported.wav" => lisas[i].read;

spork ~ handleFire();
fun void handleFire() {
  true => int hc;
  while (true) {
    !hc => hc;
    if (hc) for (int i; i < N; i++) me.dir() + "../samples/hc" + i + ".wav" => lisas[i].read;
    else for (int i; i < N; i++) me.dir() + "../samples/sz" + i + ".wav" => lisas[i].read;
    fire => now;
  }
}

fun void grain(int i) {
  lisas[i] @=> LiSa @ lisa;

  lisa.getVoice() => int voice;

  if (voice > -1) {
    (current[i][1], magicMin, magicMax, 0.1, 100) => Math.map => float rate;
    (0, lisa.duration() / samp) => Math.random2f => float pos;
    (1000, 2000) => Math.random2f => float len;
    50::ms => dur up;
    50::ms => dur down;

    (current[i][1], magicMin, magicMax, 0.1, 0) => Math.map => gains[i].gain;

    (voice, rate) => lisa.rate;
    (voice, pos::ms) => lisa.playPos;
    (voice, up) => lisa.rampUp;

    len::ms => now;

    (voice, down) => lisa.rampDown;

    down => now;
  }
}

fun void grains(int i) {
  while (true) {
    if (current[i][0]) spork ~ grain(i);
    (current[i][1], magicMin, magicMax, 200, 500) => Math.map => float wait;
    wait::ms => now;
  }
}

eon => now;