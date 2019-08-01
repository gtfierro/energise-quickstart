# LPBC, SPBC Implementations for XBOS

## System Requirements

- Make sure you are on a Linux system (Ubuntu is nice)
- Install (or make sure you have installed) Python3
- Have WAVEMQ and WAVED running on the machine (see `LOCAL_SETUP.md` if you need this)
- install packages on ubuntu:
    ```
    sudo apt install python3-venv python3-dev autoconf automake build-essential libtool
    ```


## Python Requirements

- Python 3.6 or higher
- python packages:
    ```
    pip install --user pyxbos pandas
    ```

## Configuration

### SPBC and LPBC Names

SPBCs, LPBCs and uPMUs all have names. Names can contain the following characters: `a-zA-Z0-9_-`

LPBCs and SPBCs need to know the names (and channels) of the
uPMUs they want to subscribe to in order to get phasor data. SPBCs need to know the names of the LPBCs
they need to send targets to and receive status updates from.
LPBCs need to know the name of the SPBC they are listening to for phasor targets.

To create a new SPBC name, run the following script, replacing `<spbcname>` with the name of the SPBC

```
./create_spbc.sh <spbcname>
```

To create a new LPBC name, run the following script, replacing `<lpbcname>` with the name of the LPBC

```
./create_lpbc.sh <lpbcname>
```

The output of both of these scripts is a file called `<spbcname>.ent` or `<lpbcname>.ent` depending on which
script you ran. This file is needed by an SPBC or LPBC program to connect to XBOS.

### uPMUs

uPMUs publish each channel on a different WAVE "topic".

Existing uPMUs:

| name | channels |
|------|----------|
|`uPMU_0` | `L1`,`L2`,`L3`, `C1`, `C2`, `C3`|
|`uPMU_123P` | `L1`,`L2`,`L3`, `C1`, `C2`, `C3`|
|`uPMU_123` | `L1`,`L2`,`L3`, `C1`, `C2`, `C3`|
|`uPMU_4` | `L1`,`L2`,`L3`, `C1`, `C2`, `C3`|

To subscribe to channel `L1` on the first uPMU, you would use `uPMU_0/L1`.

`LX` channels are volt; `CX` channels are amp

## SPBC

### Configuration

The SPBC process takes as a configuration input a filename with the following keys:

- `namespace`: do not change
- `wavemq`: address of local wavemq agent
- `name`: name of the SPBC controller. Naming each SPBC allows us to have multiple
  parallel SPBCs in operation. LPBCs choose which SPBC they want to listen to by
  specifying this name in their own configuration.
- `entity`: the name of the local file constituting the 'identity' of this process.
  The entity file is what gives this process the permission to interact with other
  resources. File is created by `create_spbc.sh`
- `reference_channels`: a list of URIs representing the phasor channels the SPBC
  subscribes to as reference phasors

**You can supply additional keys to the configuration dicationary; these are made available
to the process in the `__init__` function**

Example:

```toml
# spbc_1.toml
namespace = "GyDX55sFnbr9yCB-mPyXsy4kAUPUY8ftpWX62s6UcnvfIQ=="
wavemq = '127.0.0.1:4516'
name = 'spbctest'
entity = 'spbctest.ent'
reference_channels = ['flexlab1/L1']
```

The SPBC expects a configuration file as an argument when it is invoked:

```bash
$ python3 spbc.py spbc_1.toml
```

### Execution

Look at `spbc.py` for an example. The `compute_and_announce` function gets called every 3 seconds
(this is configurable). This function analyzes the reference phasor information and lpbc status information
and calls `self.broadcast_target` to send computed phasor targets to LPBCs.

### Data

The SPBC has several data streams available to it as a result of its configuration.

`self.reference_phasors`: contains the most recently received phasors from each of the reference
phasor channels. This only contains the data from the most recently received phasor message,
which *does not* consist of all the data since the SPBC `compute_and_announce` was last run
The SPBC framework keeps the `self.reference_phasors` data up to date in the background.

`self.reference_phasors` is a dictionary keyed by the names of the phasor channels indicated
in the `reference_channels` configuration option. For example, if the SPBC is configured
with `reference_channels = ['flexlab1/L1','flexlab1/L2']`, then `self.reference_phasors` would
contain the following structure:

```python
self.reference_phasors = {
    'flexlab1/L1': [
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
        ... etc
    ],
    'flexlab/L2': [
        {
            "time": "1559231114799996800",
            "angle": 220.30149788923268,
            "magnitude": 10.038565948605537415
        },
        {
            "time": "1559231114899996400",
            "angle": 220.50249902851263,
            "magnitude": 10.042079225182533264
        }
    ]
}
```

`self.lpbcs`: contains the most recent LPBC statuses. By default, the SPBC subscribes to
LPBC instances it has permission to access. The SPBC framework subscribes to the
LPBC statuses in the background and transparently updates the self.lpbcs structure.
self.lpbcs is a dictionary keyed by the names of each LPBC. Each value is another dictionary
for that LPBC node, keyed by the channels for the LPBC (e.g. L1)

```python
self.lpbcs = {
    # node name
    'lpbc_1': {
        # phase names
        'L1': {
            # local time of LPBC
            'time': 1559231114799996800,
            # phasor errors of LPBC
            'phasor_errors': {
                'angle': 1.12132,
                'magnitude': 31.12093090,
                # ... and/or ...
                'P': 1.12132,
                'Q': 31.12093090,
            },
            # true if P is saturated
            'pSaturated': True,
            # true if Q is saturated
            'qSaturated': True,
            # if p_saturated is True, expect the p max value
            'pMax': 1.4,
            # if q_saturated is True, expect the q max value
            'qMax': 11.4,
        },
    },
    # etc...
}
```

## LPBC

### Configuration

The LPBC process takes as configuration input a file with the following keys

- `namespace`: do not change
- `wavemq`: address of local wavemq agent
- `name`: name of the LPBC controller. **This needs to be unique**
- `entity`: the name of the local file constituting the 'identity' of this process.
  The entity file is what gives this process the permission to interact with other
  resources. File is created by `create_lpbc.sh`
- `spbc`: the name of the SPBC this LPBC is subscribed to for phasor targets
- `local_channels`: a list of URIs representing the phasor channels the LPBC
  subscribes to as the local measurement phasors
- `reference_channels`: a list of URIs representing the phasor channels the LPBC
  subscribes to as reference phasors
- `rate`: how many seconds between executions of the LPBC (can be fractional, e.g. 0.5)

**You can supply additional keys to the configuration dicationary; these are made available
to the process in the `__init__` function**

Example:

```toml
# lpbc_1.toml

namespace = "GyDX55sFnbr9yCB-mPyXsy4kAUPUY8ftpWX62s6UcnvfIQ=="
name = 'lpbctest' # node ID for the LPBC
spbc = 'spbctest' # name of SPBC
local_channels = ['moustafa/L1']
reference_channels = ['flexlab1/L1']
entity = 'lpbctest.ent'
wavemq = '127.0.0.1:4516'
rate = 1 # number of seconds between calls to 'step'
```

The LPBC expects a configuration file as an argument when it is invoked:

```bash
$ python3 lpbc.py lpbc_1.toml
```

### Execution

Look at `lpbc.py` for an example. The `step` function gets called every 1 second
(this is configurable). This function analyzes the reference and local phasor information and current phasor targets and does whatever local control it wants.

**TODO: need to get the API information for inverters, etc from LBL**

It returns a status indicating the state of the LPBC.
The `phases` key in the `status` dictionary tells the framework which index corresponds to which phase.
It is expected that each key appears in the `status` dictionary, and that each value is a list of the appropriate length: if there are 2 phases, then each value (`V`, `delta`,`p_saturated`,`q_saturated`, `p_max`, `q_max`) should be a list of length 2.

```python
status = {}
status['phases'] = ['L1','L2']
status['phasor_errors'] = {
        'V': [1.2,2.3],        #TODO: populate this with the error
        'delta': [3.4,0.1],    #TODO: populate this with the error
    }
status['p_saturated'] = [True,False] #TODO: set to True if saturated, false otherwise
status['q_saturated'] = [True,False] #TODO: set to True if saturated, false otherwise
status['p_max'] = [10.4, None] #TODO: set to the value p saturated at; empty/None otherwise
status['q_max'] = [.51, None] #TODO: set to the value q saturated at; empty/None otherwise

return status
```

### Data

The following data is supplied on every call to `step` in the LPBC:

`local_phasors`: a list of lists of phasor data, corresponding to the
`local_channels` given in the LPBC configuration. The phasor data will
contain *all* phasor data received by the LPBC since the last time the
`step` function was run. The outer list of local phasor channels is ordered
the same as the `local_channels` configuration variable.

If `local_channels=["moustafa/L1","moustafa/L2"]`, then `local_phasors` will look like

```python
[
    # data for moustafa/L1
    [
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
    ],
    # data for moustafa/L2
    [
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
    ],
]
```

`reference_phasors`: a list of lists of phasor data, corresponding to the
`reference_channels` given in the LPBC configuration. The phasor data will
contain *all* phasor data received by the LPBC since the last time the
`step` function was run. The outer list of reference phasor channels is ordered
the same as the `reference_channels` configuration variable.



`phasor_target`: is the most recently received phasor target given by the SPBC.
The phasor target key is an array of the targets for each phase.
It is structured as follows:

```python
{
    'time': "1559231114799996800", # SPBC time in nanoseconds
    'phasor_targets': [
        {
            'nodeID': <lpbc name>,
            'channelName': 'moustafa/L1',
            'angle': 196.123,
            'magnitude': 10.2,
            'kvbase': {'value': 10},
        },
        {
            'nodeID': <lpbc name>,
            'channelName': 'moustafa/L2',
            'angle': 196.123,
            'magnitude': 10.2,
            'kvbase': {'value': 10},
        },
    ]
}
```
