from pyxbos.process import run_loop, schedule
from pyxbos.drivers import pbc
import logging
import random
logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(message)s')

class myspbc(pbc.SPBCProcess):
    """
    This is an example SPBC implementation demonstrating how to access and use
    the data available through XBOS.

    Configuration:
    - namespace: do not change
    - wavemq: address of local wavemq agent
    - name: name of the SPBC controller. Naming each SPBC allows us to have multiple
      parallel SPBCs in operation. LPBCs choose which SPBC they want to listen to by
      specifying this name in their own configuration.
    - entity: the name of the local file constituting the 'identity' of this process.
      The entity file is what gives this process the permission to interact with other
      resources
    - reference_channels: a list of URIs representing the phasor channels the SPBC
      subscribes to as reference phasors


    Data: the SPBC has several data streams available to it as a result of its configuration.
    - self.reference_phasors: contains the most recently received phasors from each of the reference
      phasor channels. This only contains the data from the most recently received phasor message,
      which *does not* consist of all the data since the SPBC "compute_and_announce" was last run
      The SPBC framework keeps the self.reference_phasors data up to date in the background.

      self.reference_phasors is a dictionary keyed by the names of the phasor channels indicated
      in the 'reference_channels' configuration option. For example, if the SPBC is configured
      with "reference_channels = ['flexlab1/L1','flexlab1/L2']", then self.reference_phasors would
      contain the following structure:

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
    - self.lpbcs: contains the most recent LPBC statuses. By default, the SPBC subscribes to
      all LPBC instances it has permission to access. The SPBC framework subscribes to the
      LPBC statuses in the background and transparently updates the self.lpbcs structure.
      self.lpbcs is a dictionary keyed by the names of each LPBC. Each value is another dictionary
      for that LPBC node, keyed by the channels for the LPBC (e.g. L1)

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
    """
    def __init__(self, cfg):
        super().__init__(cfg)

        # Create whatever instance variables + initialization you want here.
        # Pass options in using the 'cfg' dictionary

        # This particular implementation calls the self.compute_and_announce function
        # every 3 seconds; the self.compute_and_announce contains the optimization function
        # that produces the phasor target for each LPBC
        schedule(self.call_periodic(3, self.compute_and_announce))

    async def compute_and_announce(self):

        # how to loop through all LPBC statuses
        for lpbc, channels in self.lpbcs.items():
            for channel, status in channels.items():
                print('LPBC status:', lpbc,':', channel, ':', status)

        # how to loop through all reference phasor channels
        for channel, data in self.reference_phasors.items():
            print(f"Channel {channel} has {len(data) if data else 0} points")

        # you could do expensive compute to get new targets here.
        # This oculd produce some intermediate structure like so:

        # TODO: how do we communicate phase information?
        # None-padded? dicts keyed by the channel name?
        computed_targets = {
            'lpbc_1': {
                # 3 phases
                'channels': ['L1','L2','L3'],
                'V': [1.0,2.0,3.0],
                'delta': [.8, .9, .7],
                'kvbase': None,
            },
            'lpbctest': {
                'channels': ['L2'],
                'V': [1.0],
                'delta': [.8],
                'kvbase': [1],
            }
        }

        # loop through the computed targets and send them to all LPBCs:
        for lpbc_name, targets in computed_targets.items():
            await self.broadcast_target(lpbc_name, targets['channels'], \
                            targets['V'], targets['delta'], targets['kvbase'])

cfg = {
    'namespace': "GyDX55sFnbr9yCB-mPyXsy4kAUPUY8ftpWX62s6UcnvfIQ==",
    'wavemq': '127.0.0.1:4516',
    'name': 'spbctest',
    'entity': 'spbctest.ent',
    'reference_channels': ['flexlab1/L1','flexlab1/L2']
}
spbc_instance = myspbc(cfg)
run_loop()
