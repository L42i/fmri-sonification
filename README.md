# sonification

This  bla bla


this instruction is for running the project on a Ubuntu studio (debian system)


- what do we need?

controller, ....


## Install and Setup

In the desktop audio settings, use KT audio and select "pro audio"



### Python Setup

Create and activate vit env:

    $ python3 -m venv venv

    $ source venv/bin/activate


Install Depen:


    $ pip install -r requirements.txt

### Chuck

    $ sudo apt install chuck



### Reaper/ICST/IEM





## Running the Project


### qpwgraph

activate the connection file:

![](graphics/qpwgraph.png)    

(needed for jack connection management)



### Plugins


From:    https://github.com/schweizerweb/icst-ambisonics-plugins/releases




### Reaper

1: Set channels to 64

![alt text](graphics/reaper_channels.png)


### Chuck 


    $ cd synth

    $ chuck -c53 --driver:JACK soundengine.ck 


Output should be:

        Loaded file: audio 1/a/high/raspy a high.wav 
        Sample index: 0 
        Total samples: 251752 
        Actual sample rate: 48000.000000 
        maxStartSample: 250552 
        sampleVersion: 1 
        OSC port: 8000

### Studio-Specific

(Couch 204)

MIDAS:

- set input to AES50A




```

```
