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
    """
    def __init__(self, cfg):
        super().__init__(cfg)

        # Create whatever instance variables + initialization you want here.
        # Pass options in using the 'cfg' dictionary

        self.Pcmd = 0
        self.Qcmd = 0

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

        print('channels: ', [chan['channelName'] for chan in c37_frame['phasorChannels']])
        c37_data = c37_frame['phasorChannels'][0]['data']
        for reading in c37_data:
            timestamp = pd.to_datetime(int(reading['time']), utc=True).tz_convert('US/Pacific')
            angle = reading['angle']
            magnitude = reading['magnitude']
            print(f"Got angle {angle} magnitude {magnitude} at {timestamp}")

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
        'namespace': "GyDX55sFnbr9yCB-mPyXsy4kAUPUY8ftpWX62s6UcnvfIQ==",
        'name': 'lpbctest', # name of lpbc
        'spbc': 'spbctest', # name of SPBC
        'upmu': 'L1', # name + other info for uPMU
        'entity': 'lpbctest.ent',
        'wavemq': '172.17.0.1:9516',
        'rate': 1, # number of seconds between calls to 'step'
        }
lpbc1 = democontroller(cfg)
run_loop()
