# arcade_visualiser.py

import arcade
import time

from env import FindingWillEnv
from agent import RandomJoyceAgent
import fw_config as config

# ================== WINDOW CONFIG ==================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 560
SCREEN_TITLE = "Finding Will — RL Visualization (Arcade)"

ENERGY_BAR_WIDTH = 180
ENERGY_BAR_HEIGHT = 12


# ================== MAIN VIEW ==================
class FindingWillView(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/60)

        # --- RL ---
        self.env = FindingWillEnv()
        self.agent = RandomJoyceAgent()
        self.obs = self.env.reset()
        self.done = False
        self.last_action = None

        # --- pacing ---
        self.step_timer = 0.0
        self.step_delay = 0.8   # seconds per RL step (IMPORTANT)

        # --- frame ---
        self.frame = 0

    # ---------- ASSET LOAD ----------
    def setup(self):
        self.textures = {
            "home": arcade.load_texture("assets/home.jpg"),
            "lab": arcade.load_texture("assets/lab.jpg"),
            "upside": arcade.load_texture("assets/upside_down.jpg"),
            "eleven": arcade.load_texture("assets/eleven.jpg"),
            "demogorgon": arcade.load_texture("assets/demogorgon.jpg"),
            "will": arcade.load_texture("assets/will.jpg"),
        }

    # ---------- UPDATE LOOP ----------
    def on_update(self, delta_time):
        if self.done:
            return

        self.step_timer += delta_time

        # Only step the RL environment every `step_delay`
        if self.step_timer >= self.step_delay:
            self.step_timer = 0.0

            action = self.agent.act(self.obs)
            self.obs, reward, self.done, info = self.env.step(action)
            self.last_action = action

        self.frame += 1

    # ---------- DRAW ----------
    def on_draw(self):
        arcade.start_render()

        time_left, belief, signal, fatigue, stress, lab = self.obs

        # ----- BACKGROUND SELECTION -----
        if self.last_action == config.SEARCH_LAB:
            bg = self.textures["lab"]
        elif self.last_action == config.ENTER_UPSIDE_DOWN:
            bg = self.textures["upside"]
        else:
            bg = self.textures["home"]

        arcade.draw_lrwh_rectangle_textured(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, bg
        )

        # ----- HUD (TOP) -----
        self.draw_bar(20, SCREEN_HEIGHT - 30, fatigue, "Eleven", arcade.color.YELLOW)
        self.draw_bar(240, SCREEN_HEIGHT - 30, stress, "Stress", arcade.color.RED)
        self.draw_bar(460, SCREEN_HEIGHT - 30, lab, "Lab", arcade.color.BLUE)

        # ----- LIGHTS -----
        self.draw_lights(signal, belief, stress, self.last_action == config.READ_LIGHTS)

        # ----- ELEVEN -----
        if self.last_action == config.USE_ELEVENS_POWER:
            arcade.draw_texture_rectangle(
                140, 160,
                180, 260,
                self.textures["eleven"]
            )

        # ----- DEMOGORGON -----
        if self.last_action in (config.SET_BAIT, config.ENTER_UPSIDE_DOWN):
            alpha = min(255, int(60 + stress * 20))
            self.textures["demogorgon"].alpha = alpha

            arcade.draw_texture_rectangle(
                SCREEN_WIDTH - 180, 180,
                260, 320,
                self.textures["demogorgon"]
            )

        # ----- WILL (ONLY WHEN FOUND) -----
        if belief >= 1.0:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, 170,
                160, 240,
                self.textures["will"]
            )

        # ----- SPLIT TEAM EFFECT -----
        if self.last_action == config.SPLIT_TEAM:
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                SCREEN_WIDTH / 2, SCREEN_HEIGHT,
                (0, 0, 0, 80)
            )
            arcade.draw_line(
                SCREEN_WIDTH / 2, 0,
                SCREEN_WIDTH / 2, SCREEN_HEIGHT,
                arcade.color.RED, 3
            )

        # ----- UPSIDE DOWN ATMOSPHERE -----
        if self.last_action == config.ENTER_UPSIDE_DOWN:
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                (90, 40, 120, 90)
            )

        # ----- ACTION LABEL -----
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH / 2, 24,
            SCREEN_WIDTH, 36,
            (10, 10, 20, 220)
        )

        arcade.draw_text(
            f"Action: {config.ACTION_NAMES.get(self.last_action, '---')}",
            20, 12,
            arcade.color.WHITE, 14
        )

    # ---------- UI HELPERS ----------
    def draw_bar(self, x, y, value, label, color):
        arcade.draw_rectangle_outline(
            x + ENERGY_BAR_WIDTH / 2, y,
            ENERGY_BAR_WIDTH, ENERGY_BAR_HEIGHT,
            arcade.color.WHITE
        )

        filled = max(0, min(value / 10, 1.0))
        arcade.draw_rectangle_filled(
            x + (ENERGY_BAR_WIDTH * filled) / 2, y,
            ENERGY_BAR_WIDTH * filled, ENERGY_BAR_HEIGHT,
            color
        )

        arcade.draw_text(label, x, y - 14, arcade.color.WHITE, 12)

    def draw_lights(self, signal, belief, stress, active):
        base_x = 140
        y = 260

        for i in range(10):
            x = base_x + i * 32

            if i < signal:
                flicker = arcade.rand_in_circle((0, 0), 1 + stress)[1] if active else 0
                intensity = int(150 + belief * 100)

                arcade.draw_circle_filled(
                    x,
                    y + flicker,
                    7,
                    (255, intensity, 120)
                )
            else:
                arcade.draw_circle_outline(
                    x, y,
                    5,
                    arcade.color.DARK_OLIVE_GREEN
                )


# ================== RUN ==================
def main():
    window = FindingWillView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
