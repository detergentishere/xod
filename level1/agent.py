# agent.py

import random
import fw_config as config

class ExploratoryJoyceAgent:
    """
    Stochastic exploratory agent.
    Tries to cover all actions while reacting to state.
    """

    def __init__(self, epsilon=0.25):
        self.epsilon = epsilon
        self.action_counts = {a: 0 for a in config.ACTION_NAMES}

    def act(self, obs):
        time_left, belief, signal, fatigue, stress, lab = obs

        # --- Pure exploration sometimes ---
        if random.random() < self.epsilon:
            action = random.choice(list(config.ACTION_NAMES.keys()))
            self.action_counts[action] += 1
            return action

        # --- Priority-based reasoning ---
        if belief < 0.3:
            if fatigue < 6:
                action = config.USE_ELEVENS_POWER
            elif signal > 3:
                action = config.READ_LIGHTS
            else:
                action = config.SET_BAIT

        elif belief < 0.7:
            if lab < 6:
                action = config.SEARCH_LAB
            else:
                action = config.READ_LIGHTS

        else:
            # High belief → risky confirmation
            if stress < 6:
                action = config.ENTER_UPSIDE_DOWN
            else:
                action = config.SPLIT_TEAM

        # Encourage under-used actions
        least_used = min(self.action_counts, key=self.action_counts.get)
        if self.action_counts[least_used] == 0:
            action = least_used

        self.action_counts[action] += 1
        return action
