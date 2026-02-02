# arcade_visualiser.py

import arcade
from env import FindingWillEnv
from agent import RandomJoyceAgent
import fw_config as config

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 560
SCREEN_TITLE = "Finding Will — RL Visualization"

class FindingWillView(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.env = FindingWillEnv()
        self.agent = RandomJoyceAgent()
        self.obs = self.env.reset()
        self.last_action = None
        self.timer = 0
        self.delay = 0.8

    def setup(self):
        self.bg_home = arcade.load_texture("assets/home.jpg")
        self.bg_lab = arcade.load_texture("assets/lab_bg.jpg")
        self.bg_upside = arcade.load_texture("assets/upside_down.jpg")

        # ⚠️ THESE MUST BE PNGs WITH TRANSPARENCY
        self.eleven = arcade.load_texture("assets/eleven.jpg")
        self.demo = arcade.load_texture("assets/demogorgon.jpg")
        self.will = arcade.load_texture("assets/will.jpg")

    def on_update(self, dt):
        self.timer += dt
        if self.timer > self.delay:
            self.timer = 0
            self.last_action = self.agent.act(self.obs)
            self.obs, _, done, _ = self.env.step(self.last_action)
            if done:
                self.obs = self.env.reset()

    def on_draw(self):
        arcade.start_render()

        bg = self.bg_home
        if self.last_action == config.SEARCH_LAB:
            bg = self.bg_lab
        elif self.last_action == config.ENTER_UPSIDE_DOWN:
            bg = self.bg_upside

        arcade.draw_texture_rect(SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2,SCREEN_WIDTH,SCREEN_HEIGHT,bg)


        if self.last_action == config.USE_ELEVENS_POWER:
            arcade.draw_texture_rectangle(140, 150, 180, 260, self.eleven)

        if self.last_action in (config.SET_BAIT, config.ENTER_UPSIDE_DOWN):
            arcade.draw_texture_rectangle(SCREEN_WIDTH - 180, 170, 260, 320, self.demo)

        if self.obs[1] >= 1.0:
            arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, 160, 160, 240, self.will)

        arcade.draw_text(
            f"Action: {config.ACTION_NAMES.get(self.last_action, '---')}",
            20, 20, arcade.color.WHITE, 14
        )

def main():
    app = FindingWillView()
    app.setup()
    arcade.run()

if __name__ == "__main__":
    main()
