# arcade_visualiser.py
# Arcade 3.x – Stable, Cinematic, Single-World Visualiser

import arcade
import math
import fw_config as config
from env import FindingWillEnv
from agent import ExploratoryJoyceAgent

# ---------------- CONFIG ----------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 560
SCREEN_TITLE = "Finding Will"

HUD_HEIGHT = 70
STEP_DELAY = 0.75

BAR_WIDTH = 170
BAR_HEIGHT = 12


# ---------------- HELPERS ----------------
def lerp(a, b, t=0.12):
    return a + (b - a) * t


def clamp(x, lo=0, hi=1):
    return max(lo, min(x, hi))


# ---------------- WINDOW ----------------
class FindingWillView(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # 🔧 CRITICAL: fix white background + prevent leaks
        self.background_color = (8, 10, 15)

        # RL
        self.env = FindingWillEnv()
        self.agent = ExploratoryJoyceAgent(epsilon=0.35)
        self.obs = self.env.reset()

        self.last_action = None
        self.episode_done = False
        self.outcome = None

        self.step_timer = 0.0

        # 🔧 FIX: do NOT use self.time (reserved in arcade.Window)
        self.t_clock = 0.0

        # Smooth HUD values
        self.ui_belief = 0.0
        self.ui_fatigue = 0.0
        self.ui_stress = 0.0
        self.ui_lab = 0.0

    # ---------------- ASSETS ----------------
    def setup(self):
        # Backgrounds (world)
        self.bg_home = arcade.load_texture("assets/home.jpg")
        self.bg_lab = arcade.load_texture("assets/lab_bg.jpg")
        self.bg_upside = arcade.load_texture("assets/upside_down.jpg")

        # Characters (MUST be PNG with transparency)
        self.eleven = arcade.load_texture("assets/eleven.png")
        self.demogorgon = arcade.load_texture("assets/demogorgan.png")
        self.will = arcade.load_texture("assets/will.png")

    # ---------------- UPDATE ----------------
    def on_update(self, delta_time):
        self.t_clock += delta_time

        if not self.episode_done:
            self.step_timer += delta_time
            if self.step_timer >= STEP_DELAY:
                self.step_timer = 0.0

                self.last_action = self.agent.act(self.obs)
                self.obs, _, done, _ = self.env.step(self.last_action)

                if done:
                    self.episode_done = True
                    self.outcome = "SUCCESS" if self.obs[1] >= 1.0 else "FAIL"

        # Smooth HUD interpolation
        _, belief, _, fatigue, stress, lab = self.obs
        self.ui_belief = lerp(self.ui_belief, belief)
        self.ui_fatigue = lerp(self.ui_fatigue, fatigue)
        self.ui_stress = lerp(self.ui_stress, stress)
        self.ui_lab = lerp(self.ui_lab, lab)

    # ---------------- DRAW ----------------
    def on_draw(self):
        self.clear()

        # -------- BASE VOID (prevents white bleed) --------
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            (8, 10, 15)
        )

        # -------- BASE WORLD --------
        arcade.draw_texture_rect(
            self.bg_home,
            arcade.LBWH(-2, -2, SCREEN_WIDTH + 4, SCREEN_HEIGHT + 4)
        )

        # -------- ATMOSPHERIC OVERLAYS (same world) --------
        if self.last_action == config.SEARCH_LAB:
            arcade.draw_texture_rect(
                self.bg_lab,
                arcade.LBWH(-2, -2, SCREEN_WIDTH + 4, SCREEN_HEIGHT + 4)
            )

        if self.last_action == config.ENTER_UPSIDE_DOWN:
            arcade.draw_texture_rect(
                self.bg_upside,
                arcade.LBWH(-2, -2, SCREEN_WIDTH + 4, SCREEN_HEIGHT + 4)
            )

            fog_alpha = 80 + 30 * math.sin(self.t_clock * 2)
            arcade.draw_lbwh_rectangle_filled(
                0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
                (90, 40, 130, int(fog_alpha))
            )

        # -------- CHARACTERS (IN SAME WORLD) --------
        arcade.draw_texture_rect(
            self.eleven,
            arcade.LBWH(40, 40, 180, 260)
        )

        if self.ui_stress > 4:
            wobble = math.sin(self.t_clock * 4) * 4
            arcade.draw_texture_rect(
                self.demogorgon,
                arcade.LBWH(740 + wobble, 40, 240, 300)
            )

        if self.ui_belief >= 0.95:
            arcade.draw_texture_rect(
                self.will,
                arcade.LBWH(420, 40, 160, 240)
            )

        # -------- VIGNETTE (unifies scene) --------
        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
            (0, 0, 0, 40)
        )

        # -------- HUD --------
        arcade.draw_lbwh_rectangle_filled(
            0, SCREEN_HEIGHT - HUD_HEIGHT,
            SCREEN_WIDTH, HUD_HEIGHT,
            (12, 12, 20, 235)
        )

        self.draw_bar(60,  SCREEN_HEIGHT - 40, self.ui_fatigue / 10, "ELEVEN", (230, 200, 120))
        self.draw_bar(280, SCREEN_HEIGHT - 40, self.ui_stress  / 10, "STRESS", (220, 80, 80))
        self.draw_bar(500, SCREEN_HEIGHT - 40, self.ui_lab     / 10, "LAB",    (120, 170, 240))
        self.draw_bar(720, SCREEN_HEIGHT - 40, self.ui_belief,       "WILL",   (130, 220, 160))

        arcade.draw_text(
            f"{config.ACTION_NAMES.get(self.last_action, '---')}",
            40, SCREEN_HEIGHT - 64,
            arcade.color.WHITE_SMOKE, 14
        )

        # -------- END OVERLAY --------
        if self.episode_done:
            arcade.draw_lbwh_rectangle_filled(
                0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
                (0, 0, 0, 190)
            )
            arcade.draw_text(
                "WILL IS FOUND" if self.outcome == "SUCCESS" else "MISSION FAILED",
                SCREEN_WIDTH // 2 - 220,
                SCREEN_HEIGHT // 2,
                arcade.color.GREEN if self.outcome == "SUCCESS" else arcade.color.RED,
                32,
                bold=True
            )

    # ---------------- HUD BAR ----------------
    def draw_bar(self, x, y, frac, label, color):
        frac = clamp(frac)

        arcade.draw_lbwh_rectangle_filled(
            x, y, BAR_WIDTH, BAR_HEIGHT,
            (40, 40, 50)
        )
        arcade.draw_lbwh_rectangle_filled(
            x, y, BAR_WIDTH * frac, BAR_HEIGHT,
            color
        )
        arcade.draw_text(
            label,
            x, y + 18,
            arcade.color.WHITE, 12
        )


# ---------------- RUN ----------------
def main():
    window = FindingWillView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
