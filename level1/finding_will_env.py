# finding_will_env.py
import gymnasium as gym
from gymnasium import spaces
import numpy as np

TOTAL_DEMOS = 6
MAX_STEPS = 25

PORTAL_THRESHOLD = 0.40
STEP_SIZE = 1.0 / (TOTAL_DEMOS + 2)

class FindWillEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.action_space = spaces.Box(0.0, 1.0, shape=(2,), dtype=np.float32)

        # obs:
        # [progress, eleven_power, joyce_power, known_frac, threat, demo_index_norm]
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.2,
            shape=(6,),
            dtype=np.float32
        )

        self.reset()

    def reset(self, seed=None, options=None):
        self.progress = 0.0
        self.steps = 0

        self.eleven_power = 1.0
        self.joyce_power = 1.0

        self.in_upside_down = False

        # 🔥 STOCHASTIC DEMOGORGONS
        self.demos = [
            {
                "known": False,
                "cleared": False,
                "strength": np.random.uniform(0.8, 1.2)  # hidden difficulty
            }
            for _ in range(TOTAL_DEMOS)
        ]

        self.current_index = 0
        return self._obs(), {}

    def _obs(self):
        known_frac = sum(d["known"] for d in self.demos) / TOTAL_DEMOS
        threat = (
            1.0
            if self.current_index < TOTAL_DEMOS
            and not self.demos[self.current_index]["cleared"]
            else 0.0
        )

        return np.array([
            self.progress,
            self.eleven_power,
            self.joyce_power,
            known_frac,
            threat,
            self.current_index / TOTAL_DEMOS
        ], dtype=np.float32)

    def step(self, action):
        self.steps += 1
        search, fight = action
        done = False
        reward = 0.0
        success = False

        # ---------------- SEARCH (IMPERFECT INFO) ----------------
        if search > 0.6 and self.eleven_power > 0.1:
            for d in self.demos:
                if not d["known"]:
                    if np.random.rand() < 0.75:  # 🔥 noisy scan
                        d["known"] = True
                    self.eleven_power -= 0.06
                    self.joyce_power -= 0.01
                    break

        # ---------------- FIGHT ----------------
        if self.current_index < TOTAL_DEMOS:
            demo = self.demos[self.current_index]

            if not demo["cleared"] and fight > 0.6:
                difficulty = demo["strength"]

                if demo["known"]:
                    self.eleven_power -= 0.07 * difficulty
                    self.joyce_power -= 0.05 * difficulty
                else:
                    self.eleven_power -= 0.12 * difficulty
                    self.joyce_power -= 0.10 * difficulty

                demo["cleared"] = True

            elif not demo["cleared"]:
                # 🔥 reward restraint stochastically
                self.eleven_power += np.random.uniform(0.02, 0.06)

        # ---------------- MOVE ----------------
        if (
            self.current_index >= TOTAL_DEMOS
            or self.demos[self.current_index]["cleared"]
        ):
            self.progress += STEP_SIZE
            self.current_index += 1

        # ---------------- PORTAL ----------------
        if self.progress >= 0.8 and not self.in_upside_down:
            combined = self.eleven_power + self.joyce_power
            if combined >= PORTAL_THRESHOLD:
                self.in_upside_down = True
                self.eleven_power -= 0.10
                self.joyce_power -= 0.10
            else:
                self.progress -= STEP_SIZE * 0.5

        # ---------------- TERMINATION ----------------
        if self.progress >= 1.0 or self.steps >= MAX_STEPS:
            done = True
            reward = self.eleven_power + self.joyce_power
            success = reward >= PORTAL_THRESHOLD

        self.eleven_power = np.clip(self.eleven_power, 0.0, 1.2)
        self.joyce_power = np.clip(self.joyce_power, 0.0, 1.2)

        return self._obs(), reward, done, False, {
            "success": success,
            "final_power": reward,
            "steps": self.steps
        }
