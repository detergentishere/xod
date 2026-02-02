# finding_will_env.py
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import math
import random
from enum import Enum

MAX_MOVES = 25

USE_ELEVEN_THRESHOLD = 0.6
USE_LIGHT_THRESHOLD = 0.4
USE_DEMOGORGAN_THRESHOLD = 0.7


class World(Enum):
    HOME = 0
    LAB = 1
    UPSIDE_DOWN = 2


class Eleven:
    def __init__(self):
        self.psychic_field = 0.0
        self.strain = 0.0
        self.used = False

    def update(self, force):
        self.used = abs(force) > USE_ELEVEN_THRESHOLD
        self.psychic_field += force * 0.08
        self.psychic_field *= 0.97
        self.strain += abs(force) * 0.05
        self.strain *= 0.99


class Lights:
    def __init__(self):
        self.phase = random.uniform(0, 2 * math.pi)
        self.signal = 0.3
        self.used = False

    def update(self, belief, force):
        self.used = abs(force) > USE_LIGHT_THRESHOLD
        if self.used:
            self.phase += 0.9
        self.signal = 0.3 + 0.7 * belief


class Demogorgon:
    def __init__(self):
        self.visible = False

    def update(self, stress):
        self.visible = stress > USE_DEMOGORGAN_THRESHOLD


class FindingWillEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0], dtype=np.float32),
            high=np.array([1.0, 1.0], dtype=np.float32),
            dtype=np.float32
        )

        self.observation_space = spaces.Box(
            low=0.0,
            high=1.5,
            shape=(3,),
            dtype=np.float32
        )

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.belief = 0.2
        self.stress = 0.1
        self.moves_left = MAX_MOVES

        self.eleven = Eleven()
        self.lights = Lights()
        self.demogorgon = Demogorgon()
        self.world = World.HOME

        return self._get_obs(), {}

    def _get_obs(self):
        return np.array([self.belief, self.stress, self.eleven.strain], dtype=np.float32)

    def step(self, action):
        force, risk = float(action[0]), float(action[1])
        self.moves_left -= 1

        self.eleven.update(force)
        self.lights.update(self.belief, force)
        self.demogorgon.update(self.stress)

        self.belief += (
            0.05 * self.eleven.psychic_field +
            (0.07 if self.lights.used else 0.0) -
            0.03 * self.stress
        )
        self.belief = np.clip(self.belief, 0, 1)

        self.stress += abs(risk) * 0.05
        self.stress *= 0.98

        if self.stress > 0.75:
            self.world = World.UPSIDE_DOWN
        elif self.eleven.used:
            self.world = World.LAB
        else:
            self.world = World.HOME

        reward = self.belief - self.stress
        done = False
        success = False

        if self.belief >= 1.0:
            reward += 100
            done = True
            success = True

        if self.moves_left <= 0:
            done = True

        return self._get_obs(), reward, done, False, {
            "moves_left": self.moves_left,
            "success": success
        }
