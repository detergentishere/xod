# env.py

import numpy as np
import fw_config as config
from dynamics import WorldState, apply_action

class FindingWillEnv:
    def reset(self):
        self.world = WorldState()
        self.state = [
            config.MAX_STEPS,
            0.2,
            3,
            0,
            1,
            0
        ]
        return np.array(self.state, dtype=np.float32)

    def step(self, action):
        self.state, reward, done = apply_action(
            action, self.state, self.world
        )
        return np.array(self.state, dtype=np.float32), reward, done, {}
