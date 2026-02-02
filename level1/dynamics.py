# dynamics.py

import random
import fw_config as config


class WorldState:
    """
    Hidden internal world state (not observed by agent)
    """
    def __init__(self):
        self.will_location_signal = random.uniform(0.3, 0.7)
        self.portal_stability = random.uniform(0.5, 1.0)


def clamp(x, low=0.0, high=1.0):
    return max(low, min(high, x))


def apply_action(action, obs, world):
    reward = config.STEP_PENALTY

    time_left, belief, signal, fatigue, stress, lab = obs

    if action == config.USE_ELEVENS_POWER:
        belief += max(0.0, 0.15 - 0.02 * fatigue) * world.will_location_signal
        fatigue += 2
        reward += config.BELIEF_REWARD

    elif action == config.READ_LIGHTS:
        belief += clamp(signal / 20 + random.uniform(-0.1, 0.1) * stress)
        reward += config.CLUE_REWARD

    elif action == config.SEARCH_LAB:
        if random.random() < 0.4:
            belief += 0.2
            reward += config.CLUE_REWARD
        lab += 2

    elif action == config.ENTER_UPSIDE_DOWN:
        belief += 0.3 * world.portal_stability
        stress += 3
        reward += config.CLUE_REWARD

    elif action == config.SPLIT_TEAM:
        belief += 0.1
        stress += random.choice([0, 2])
        reward += config.BELIEF_REWARD

    elif action == config.SET_BAIT:
        signal += 2
        stress += 1

    belief = clamp(belief)
    signal = min(signal, config.MAX_SIGNAL)
    fatigue = min(fatigue, config.MAX_FATIGUE)
    stress = min(stress, config.MAX_STRESS)
    lab = min(lab, config.MAX_LAB_ATTENTION)

    time_left -= 1

    done = False
    if belief >= 1.0:
        reward += config.SUCCESS_REWARD
        done = True
    elif time_left <= 0 or stress >= config.MAX_STRESS:
        reward += config.FAILURE_PENALTY
        done = True

    return [time_left, belief, signal, fatigue, stress, lab], reward, done
