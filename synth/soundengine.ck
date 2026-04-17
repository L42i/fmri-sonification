//------------------------------------------------------------
// 53-grain OSC-controlled looping granular engine
//
//------------------------------------------------------------


[
    "audio 1/a/high/raspy a high.wav",
    "audio 1/a/high/breathy a high.wav",
    "audio 1/a/high/supported a high.wav",
    "audio 1/a/mid/raspy a mid.wav",
    "audio 1/a/mid/breathy a mid.wav",
    "audio 1/a/mid/supported a mid.wav",
    "audio 1/a/low/Raspy a low.wav",
    "audio 1/a/low/breathy a low.wav",
    "audio 1/a/low/Supported a low.wav"
] @=> string sampleFiles[];

5 => int sampleIndex;
sampleFiles[sampleIndex] => string filename;

// OSC port
8000 => int OSC_PORT;

// grain settings
53 => int NUM_GRAINS;
25::ms => dur grainDur;
4.0::ms => dur grainAttack;

50::ms => dur grainInterval;


float grainVolumes[NUM_GRAINS];
for (0 => int i; i < NUM_GRAINS; i++)
{
    0.3 => grainVolumes[i];
}


// =========================
// load source once for analysis
// =========================

SndBuf src => blackhole;
filename => src.read;

src.samples() => int totalSamples;

if (totalSamples <= 0)
{
    <<< "ERROR: could not load file:", filename >>>;
    me.exit();
}

(grainDur / samp) $ int => int grainSamples;
totalSamples - grainSamples => int maxStartSample;

if (maxStartSample < 0)
{
    <<< "ERROR: file shorter than one grain." >>>;
    me.exit();
}

<<< "Loaded file:", filename >>>;
<<< "Total samples:", totalSamples >>>;
<<< "Actual sample rate:", second / samp >>>;
<<< "OSC port:", OSC_PORT >>>;


// =========================
// choose 53 fixed random grain starts
// =========================

int grainStarts[NUM_GRAINS];

for (0 => int i; i < NUM_GRAINS; i++)
{
    Math.random2(0, maxStartSample) => grainStarts[i];
    <<< "grain", i, "start sample =", grainStarts[i] >>>;
}


// =========================
// OSC receiver
// 53 addresses:
//
// 1 interval address:
//   /grainInterval
//
// all messages carry one float
// =========================

OscRecv recv;
OSC_PORT => recv.port;
recv.listen();


// =========================
// helper: clamp float
// =========================

fun float clamp01(float x)
{
    if (x < 0.0) return Math.min (1.0, - x);
    if (x > 1.0) return 1.0;
    return x;
}


// =========================
// OSC listener for one volume
// =========================

fun void volumeListener(int index)
{
    OscEvent oe;
    recv.event("/controller" + index + ", f") @=> oe;
    <<<oe.getFloat()>>>;

    while (true)
    {
        oe => now;

        while (oe.nextMsg() != 0)
        {
            clamp01(oe.getFloat()) => grainVolumes[index];
        }
    }
}


// =========================
// OSC listener for interval
// unit: milliseconds
// e.g. send 20.0 means 20 ms
// =========================

fun void intervalListener()
{
    OscEvent oe;
    recv.event("/controller/yoke, f") @=> oe;

    while (true)
    {
        oe => now;

        while (oe.nextMsg() != 0)
        {
            oe.getFloat() => float intervalMs;

            intervalMs * 100 => intervalMs;

            if (intervalMs < 5.0) 5.0 => intervalMs;

            intervalMs::ms => grainInterval;
        }
    }
}

fun void attackListener()
{
    OscEvent oe;
    recv.event("/control/throttle1, f") @=> oe;

    while (true)
    {
        oe => now;

        while (oe.nextMsg() != 0)
        {
            oe.getFloat() => float attackMs;

            if (attackMs < 1.0) 1.0 => attackMs;

            if (attackMs > 20.0) 20.0 => attackMs;

            attackMs::ms => grainAttack;

            <<< "Updated attack =", attackMs, "ms" >>>;
        }
    }
}


fun void sampleIndexListener()
{
    OscEvent oe;
    recv.event("/control/throttle2, f") @=> oe;

    while (true)
    {
        oe => now;

        while (oe.nextMsg() != 0)
        {
            oe.getFloat() => float thisIndex;

            Math.floor(thisIndex * 9) $ int => sampleIndex;

            sampleFiles[sampleIndex] => filename;

            <<< "Updated sample =", sampleIndex >>>;
        }
    }
}
// =========================
// one looping grain voice
// each voice owns:
//   - its own SndBuf
//   - its own ADSR
//   - one fixed startSample
//
// it keeps retriggering forever
// =========================

fun void grainVoice(int index, int startSample)
{
    SndBuf g => ADSR env => dac;

    -1 => int lastSampleIndex;

    5::ms => dur decay;
    0.8 => float sustainLevel;
    5::ms => dur release;

    index::samp => now;

    while (true)
    {
        if (sampleIndex != lastSampleIndex)
        {
            sampleFiles[sampleIndex] => g.read;
            sampleIndex => lastSampleIndex;

            if (g.samples() <= 0)
            {
                <<< "ERROR: failed to load sample", sampleIndex >>>;
                100::ms => now;
                continue;
            }
        }

        clamp01(grainVolumes[index]) => g.gain;
        Math.random2(0, g.samples() - 1) => g.pos;

        grainAttack => dur attack;

        if (grainDur < attack + decay + release)
        {
            1::ms => attack;
            1::ms => decay;
            1::ms => release;
        }

        env.set(attack, decay, sustainLevel, release);

        env.keyOn();
        grainDur - release => now;
        env.keyOff();
        release => now;

        grainInterval => now;
    }
}

// =========================
// start OSC listeners
// =========================

for (0 => int i; i < NUM_GRAINS; i++)
{
    spork ~ volumeListener(i);
}

spork ~ intervalListener();
spork ~ attackListener();
spork ~ sampleIndexListener();


// =========================
// start 53 looping grain voices
// =========================

for (0 => int i; i < NUM_GRAINS; i++)
{
    spork ~ grainVoice(i, grainStarts[i]);
}


// =========================
// keep VM alive forever
// =========================

while (true)
{
    1::second => now;
}