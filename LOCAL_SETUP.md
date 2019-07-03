# LPBC, SPBC Implementations for XBOS

## Setup

- Make sure you are on a Linux system (Ubuntu is nice)
- Install (or make sure you have installed) Python3
- Install (or make sure you have installed) docker
    - This is easier if you [add your user to the `docker` group to avoid using sudo](https://docs.docker.com/install/linux/linux-postinstall/)

This should be accomplished with the following (some dependencies required for building the `jq` dependency for the `pyxbos` package):

```bash
apt install docker.io python3-venv python3-dev autoconf automake build-essential libtool
```

Run the following in the terminal to get the basic XBOS services runninng

```bash
git clone github.com/gtfierro/energise-quickstart
cd energise-quickstart
source environment.sh
./run.sh
```
After running the `run.sh` script above, there should be two docker containers running: `energise-wavemq` and `energise-waved`.

Setup a Python environment:

```bash
python3 -m venv venv # do once
. venv/bin/activate # every time you want to run a script
pip install pyxbos pandas # do once
```

Currently the LPBC needs a running uPMU and SPBC in order to function.
The uPMU is already publishing some dummy data and requires no additional setup, but you do need to get an SPBC working.


## Creating Entities for SPBC + LPBC

We need to create an XBOS entity for the SPBC and LPBC.

```
source environment.sh
./create_lpbc.sh lpbctest
./create_spbc.sh spbctest
```

`lpbctest` and `spbctest` above are the names of the LPBC and SPBC controller instances, respectively.
These names are configured in the `cfg` dictionary found in the implementations of the LPBC and SPBC (`lpbc.py` and `spbc.py`, respectively). You do not need to change anything for using the `lpbctest` and `spbctest` names above, but keep in mind that deviating from those names will require changing the file's configuration.

It is recommended that you eventually change these names. If we wanted to call the LPBC instance `lpbc-inverter-1` and the SPBC instance `spbc-static`, then we would do the following.

Run this in the shell:

```
source environment.sh
./create_lpbc.sh lpbc-inverter-1
./create_spbc.sh spbc-static
```

In `lpbc.py`,

```python
# ... snip ...
cfg = {
        'namespace': "GyDX55sFnbr9yCB-mPyXsy4kAUPUY8ftpWX62s6UcnvfIQ==",
        'name': 'lpbc-inverter-1', # name of lpbc          <----- CHANGED
        'spbc': 'spbc-static', # name of SPBC              <----- CHANGED
        'upmu': 'L1', # name + other info for uPMU
        'entity': 'lpbc-inverter-1.ent',          #        <----- CHANGED
        'wavemq': '172.17.0.1:9516',
        'rate': 2, # number of seconds between calls to 'step'
        }
```

In `spbc.py`

```python
# ... snip ...
cfg = {
    'namespace': "GyDX55sFnbr9yCB-mPyXsy4kAUPUY8ftpWX62s6UcnvfIQ==",
    'wavemq': '172.17.0.1:9516',
    'name': 'spbc-static',      #   <----- CHANGED
    'entity': 'spbc-static.ent',#   <----- CHANGED
}
```

## Running SPBC + LPBC

Run these inside the Python virtualenv established above.

LPBC:

```
. venv/bin/activate
python lpbc.py
```

SPBC:

```
. venv/bin/activate
python spbc.py
```

### TODO:

- [ ] document how to set up entities, etc

## LPBC

LPBC is passed a C37 data frame. This looks like the following Python/JSON object.

The last item of the `data` array is the most recent uPMU reading.

**This data is for a uPMU that is not measuring a real line; data makes no sense**

```json
{
    "stationName": "ENERGIZE_1",
    "idCode": 1,
    "phasorChannels": [
        {
            "channelName": "L1MagAng",
            "unit": "Volt",
            "data": [
                {
                    "time": "1559231114000000000",
                    "angle": 196.5132440822694,
                    "magnitude": 0.03969825804233551
                },
                {
                    "time": "1559231114099999600",
                    "angle": 188.9396298022358,
                    "magnitude": 0.03955257683992386
                },
                {
                    "time": "1559231114199999200",
                    "angle": 195.676149757971,
                    "magnitude": 0.042156800627708435
                },
                {
                    "time": "1559231114299998800",
                    "angle": 192.79764849453917,
                    "magnitude": 0.03830688074231148
                },
                {
                    "time": "1559231114399998400",
                    "angle": 195.984969931104,
                    "magnitude": 0.034339841455221176
                },
                {
                    "time": "1559231114499998000",
                    "angle": 194.05622013214077,
                    "magnitude": 0.037918806076049805
                },
                {
                    "time": "1559231114599997600",
                    "angle": 193.4088138214719,
                    "magnitude": 0.032730501145124435
                },
                {
                    "time": "1559231114699997200",
                    "angle": 195.04004058018938,
                    "magnitude": 0.03850540146231651
                },
                {
                    "time": "1559231114799996800",
                    "angle": 193.30149788923268,
                    "magnitude": 0.038565948605537415
                },
                {
                    "time": "1559231114899996400",
                    "angle": 195.50249902851263,
                    "magnitude": 0.042079225182533264
                }
            ]
        }
    ]
}
```

```python
from pyxbos.process import run_loop
from pyxbos.drivers import pbc
import logging
logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
import random

class democontroller(pbc.LPBCProcess):
    """
    To implement a LPBC, subclass pbc.LPBCProcess
    and implement the step() method as documented below
    """
    def __init__(self, cfg):
        super().__init__(cfg)

        # Create whatever instance variables + initialization you want here.
        # Pass options in using the 'cfg' dictionary

        self.measured_p = 1
        self.measured_q = 1
        self.saturated = False

    def step(self, c37_frame, p_target, q_target):
        """
        Step is called every 'rate' seconds with the most recent c37 frame from the upmu
        and the latest P and Q targets given by the SPBC.

        It runs its control loop to determine the actuation, performs it is 'self.control_on' is True
        and returns the status

        C37 frame looks like

            {
                "stationName": "ENERGIZE_1",
                "idCode": 1,
                "phasorChannels": [
                    {
                        "channelName": "L1MagAng",
                        "unit": "Volt",
                        "data": [
                            {
                                "time": "1559231114799996800",
                                "angle": 193.30149788923268,
                                "magnitude": 0.038565948605537415
                            },
                            {
                                "time": "1559231114899996400",
                                "angle": 195.50249902851263,
                                "magnitude": 0.042079225182533264
                            }
                        ]
                    }
                ]
            }
        """

        print(c37_frame)

        # do measurements
        self.measured_p = random.randint(0,100)
        self.measured_q = random.randint(0,100)

        p_diff = self.measured_p - p_target
        q_diff = self.measured_q - q_target

        print(f'controller called. P diff: {p_diff}, Q diff: {q_diff}')

        if self.control_on:
            print("DO CONTROL HERE")
        

        # return error message (default to empty string), p, q and boolean saturated value
        return ("error message", self.measured_p, self.measured_q, self.saturated)

cfg = {
        'namespace': "GyCetklhSNcgsCKVKXxSuCUZP4M80z9NRxU1pwfb2XwGhg==",
        'name': 'lpbctest', # name of lpbc
        'spbc': 'spbctest', # name of SPBC
        'upmu': 'L1', # name + other info for uPMU
        'rate': 2, # number of seconds between calls to 'step'
        }
lpbc1 = democontroller(cfg)
run_loop()
```
