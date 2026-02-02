# agent.py
import numpy as np

class StrategicAgent:
    """
    Risk-aware stochastic policy.
    Makes decisions under uncertainty, not optimization.
    """

    def __init__(self):
        self.temperature = 0.25  # exploration noise

    def act(self, obs):
        progress, el_p, joyce_p, known_frac, threat, demo_idx = obs
        combined = el_p + joyce_p

        search = 0.0
        fight = 0.0

        # ---------------- THREAT ----------------
        if threat > 0.5:
            p_search = 0.6 * (1 - known_frac)
            p_fight  = 0.7 * known_frac + 0.3

            if combined < 0.6:
                p_search *= 0.4
                p_fight *= 0.8

            if np.random.rand() < p_search:
                search = 1.0
            else:
                fight = 1.0

        # ---------------- NO THREAT ----------------
        else:
            if progress < 0.5 and el_p > 0.4:
                if np.random.rand() < (0.4 - progress):
                    search = 1.0

        # ---------------- LATE GAME ----------------
        if progress > 0.8:
            search = 0.0
            fight = 1.0 if threat > 0.5 else 0.0

        # ---------------- STOCHASTICITY ----------------
        search += np.random.normal(0, self.temperature)
        fight  += np.random.normal(0, self.temperature)

        action = np.clip(np.array([search, fight]), 0.0, 1.0)
        return action
