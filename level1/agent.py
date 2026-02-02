# agent.py
import numpy as np

class ExploratoryAgent:
    def act(self, obs):
        belief, stress, strain = obs

        force = np.tanh(0.9 - belief - strain)
        risk = np.tanh(stress)

        force += np.random.normal(0, 0.25)
        risk += np.random.normal(0, 0.25)

        return np.array([force, risk], dtype=np.float32)
