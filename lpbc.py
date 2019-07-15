from pyxbos.process import run_loop
from pyxbos.drivers import pbc
import logging
logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')
import random
import pandas as pd

class democontroller(pbc.LPBCProcess):
    """
    To implement a LPBC, subclass pbc.LPBCProcess
    and implement the step() method as documented below

    Configuration:
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
    """
    def __init__(self, cfg):
        super().__init__(cfg)

        # Create whatever instance variables + initialization you want here.
        # Pass options in using the 'cfg' dictionary

    def step(self, local_phasors, reference_phasors, phasor_target):
        """
        Step is called every 'rate' seconds with the following data:
        - local_phasors: a list of lists of phasor data, corresponding to the
          'local_channels' given in the LPBC configuration. The phasor data will
          contain *all* phasor data received by the LPBC since the last time the
          'step' function was run. The outer list of local phasor channels is ordered
          the same as the 'local_channels' configuration variable.

          If 'local_channels=["L1","L2"]', then 'local_phasors' will look like

            [
                # data for L1
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
                # data for L2
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

        - reference_phasors: a list of lists of phasor data, corresponding to the
          'reference_channels' given in the LPBC configuration. The phasor data will
          contain *all* phasor data received by the LPBC since the last time the
          'step' function was run. The outer list of reference phasor channels is ordered
          the same as the 'reference_channels' configuration variable.

          The structure of the 'reference_phasors' is the same structure as 'local_phasors' above.

        - phasor_target: is the most recently received phasor target given by the SPBC.
          The phasor target key is an array of the targets for each phase.
          It is structured as follows:

            {
                'time': "1559231114799996800", # SPBC time in nanoseconds
                'phasor_targets': [
                    {
                        'nodeID': <lpbc name>,
                        'channelName': 'L1',
                        'angle': 196.123,
                        'magnitude': 10.2,
                        'kvbase': {'value': 10},
                    },
                    {
                        'nodeID': <lpbc name>,
                        'channelName': 'L2',
                        'angle': 196.123,
                        'magnitude': 10.2,
                        'kvbase': {'value': 10},
                    },
                ]
            }
        """

        for idx, local_channel in enumerate(self.local_channels):
            print(f"Local channel: Received {len(local_phasors[idx])} for channel {local_channel}")
        for idx, reference_channel in enumerate(self.reference_channels):
            print(f"Reference channel: Received {len(reference_phasors[idx])} for channel {reference_channel}")
        print(f"Got phasor targets {phasor_target}")

        # how to iterate through the phasor data
        for idx, local_channel in enumerate(self.local_channels):
            for reading in local_phasors[idx]:
                timestamp = pd.to_datetime(int(reading['time']), utc=True).tz_convert('US/Pacific')
                angle = reading['angle']
                magnitude = reading['magnitude']
                #print(f"Got angle {angle} magnitude {magnitude} at {timestamp}")

        status = {}
        # 'phases' tells us which index maps to which phase
        status['phases'] = ['L1','L2']
        status['phasor_errors'] = {
                'V': [1.2,2.3],        #TODO: populate this with the error
                'delta': [3.4,0.1],    #TODO: populate this with the error
            }
        status['p_saturated'] = [True,False] #TODO: set to True if saturated, false otherwise
        status['q_saturated'] = [True,False] #TODO: set to True if saturated, false otherwise
        status['p_max'] = [10.4, 108] #TODO: set to the value p saturated at; empty/None otherwise
        status['q_max'] = [.51, 4.1] #TODO: set to the value q saturated at; empty/None otherwise

        return status

cfg = {
        'namespace': "GyDX55sFnbr9yCB-mPyXsy4kAUPUY8ftpWX62s6UcnvfIQ==",
        'local_channels': ['flexlab1/L2'],
        'reference_channels': ['flexlab1/L1'],
        'entity': 'lpbctest.ent',
        'wavemq': '127.0.0.1:4516',
        'rate': 2, # number of seconds between calls to 'step'
        'name': 'lpbctest',
        'spbc': 'spbctest'
        }
lpbc1 = democontroller(cfg)
run_loop()
