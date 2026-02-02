# run_visual.py
import pygame
import pickle
from finding_will_env import FindWillEnv

pygame.init()

# ==================================================
# CONFIG: WHICH EPISODE TO VISUALIZE
# ==================================================
REPLAY_FILE = "best_path.pkl"
# Examples:
# "replay_ep_100.pkl"
# "replay_ep_200.pkl"
# "replay_ep_300.pkl"
# "best_path.pkl"

# ==================================================
# WINDOW
# ==================================================
WIDTH, HEIGHT = 1100, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Finding Will — Replay")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 16)
big_font = pygame.font.SysFont("consolas", 24, bold=True)

# ==================================================
# TIMING & LAYOUT
# ==================================================
STORY_DELAY = 2200
STEP_DELAY = 700
LEFT_SHIFT = -140

last_story = 0
last_step = 0

story_phase = -1
rl_active = False

# ==================================================
# LOAD REPLAY
# ==================================================
with open(REPLAY_FILE, "rb") as f:
    replay_data = pickle.load(f)

# replay_data = [(obs, action), ...]
replay_step = 0

# ==================================================
# BACKGROUNDS (FULL SCREEN)
# ==================================================
bg_intro = pygame.image.load("assets/bg/intro.jpg").convert()
bg_home = pygame.image.load("assets/bg/home.jpg").convert()
bg_fight = pygame.image.load("assets/bg/upside_down.jpg").convert()

# ==================================================
# ASSETS
# ==================================================
joyce = {
    1: pygame.image.load("assets/joyce/joyce_1.png").convert_alpha(),
    2: pygame.image.load("assets/joyce/joyce_2.png").convert_alpha(),
    3: pygame.image.load("assets/joyce/joyce_3.png").convert_alpha(),
}

eleven = {
    "idle": pygame.image.load("assets/eleven/idle.png").convert_alpha(),
    "focus": pygame.image.load("assets/eleven/focus.png").convert_alpha(),
    "attack": pygame.image.load("assets/eleven/attack.png").convert_alpha(),
}

group_img = pygame.image.load("assets/group/kids.png").convert_alpha()
will_img = pygame.image.load("assets/will/will.jpg").convert_alpha()

# ==================================================
# DEMOGORGONS (3 VARIANTS)
# ==================================================
demo_imgs = [
    pygame.transform.scale(
        pygame.image.load("assets/demo/demo_left.png").convert_alpha(),
        (240, 300)
    ),
    pygame.transform.scale(
        pygame.image.load("assets/demo/demo_center.png").convert_alpha(),
        (260, 320)
    ),
    pygame.transform.scale(
        pygame.image.load("assets/demo/demo_right.png").convert_alpha(),
        (260, 300)
    ),
]

DEMO_POS = [
    (720 + LEFT_SHIFT, 260),
    (800 + LEFT_SHIFT, 250),
    (880 + LEFT_SHIFT, 260),
]

# ==================================================
# ENV
# ==================================================
env = FindWillEnv()
obs, _ = env.reset()

done = False
info = {}
last_action = [0.0, 0.0]

# ==================================================
# HELPERS
# ==================================================
def action_text(action, obs):
    search, fight = action
    known_frac = obs[3]
    threat = obs[4]

    if search > 0.6:
        return "ACTION: Scanning (Eleven)"
    if fight > 0.6:
        if known_frac > 0.5:
            return "ACTION: Coordinated fight (Joyce + Eleven)"
        else:
            return "ACTION: Blind fight (High cost)"
    if threat > 0.5:
        return "ACTION: Holding – conserving power"
    return "ACTION: Advancing cautiously"

# ==================================================
# MAIN LOOP
# ==================================================
running = True
while running:
    now = pygame.time.get_ticks()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # --------------------------------------------------
    # STORY PROGRESSION
    # --------------------------------------------------
    if not rl_active and now - last_story > STORY_DELAY:
        story_phase += 1
        last_story = now
        if story_phase >= 5:
            rl_active = True

    # --------------------------------------------------
    # REPLAY STEP
    # --------------------------------------------------
    if rl_active and not done and now - last_step > STEP_DELAY:
        if replay_step < len(replay_data):
            _, action = replay_data[replay_step]
            obs, _, done, _, info = env.step(action)
            last_action = action
            replay_step += 1
        else:
            done = True
        last_step = now

    # --------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------
    if not rl_active:
        bg = bg_intro if story_phase < 1 else bg_home
    else:
        bg = bg_fight

    screen.blit(pygame.transform.scale(bg, (WIDTH, HEIGHT)), (0, 0))

    # ==================================================
    # HUD
    # ==================================================
    pygame.draw.rect(screen, (12, 12, 18), (0, 0, WIDTH, 100))

    if rl_active:
        screen.blit(
            font.render(action_text(last_action, obs), True, (230,230,230)),
            (30, 12)
        )

        # Eleven power
        pygame.draw.rect(screen, (60,60,60), (30, 60, 180, 10))
        pygame.draw.rect(screen, (150,130,255), (30, 60, int(180 * obs[1]), 10))
        screen.blit(font.render("Eleven", True, (230,230,230)), (30, 42))

        # Joyce power
        pygame.draw.rect(screen, (60,60,60), (240, 60, 180, 10))
        pygame.draw.rect(screen, (255,200,120), (240, 60, int(180 * obs[2]), 10))
        screen.blit(font.render("Joyce", True, (230,230,230)), (240, 42))

    # ==================================================
    # STORY SCENES
    # ==================================================
    if story_phase == -1:
        screen.blit(big_font.render("A child is missing.", True, (230,230,230)), (380, 260))

    elif story_phase == 0:
        screen.blit(joyce[1], (450 + LEFT_SHIFT, 300))
        screen.blit(big_font.render("Will is missing.", True, (230,230,230)), (380, 230))

    elif story_phase == 1:
        screen.blit(joyce[1], (450 + LEFT_SHIFT, 300))
        screen.blit(demo_imgs[1], DEMO_POS[1])
        screen.blit(big_font.render("Something is in the house.", True, (230,230,230)), (300, 230))

    elif story_phase == 2:
        screen.blit(joyce[2], (450 + LEFT_SHIFT, 300))
        screen.blit(big_font.render("Joyce calls Eleven.", True, (230,230,230)), (320, 230))

    elif story_phase == 3:
        screen.blit(eleven["idle"], (260 + LEFT_SHIFT, 300))
        screen.blit(big_font.render("Eleven listens.", True, (230,230,230)), (380, 230))

    elif story_phase == 4:
        screen.blit(group_img, (520 + LEFT_SHIFT, 300))
        screen.blit(big_font.render("The group comes together.", True, (230,230,230)), (330, 230))

    # ==================================================
    # REPLAY VISUALS
    # ==================================================
    else:
        screen.blit(joyce[3], (450 + LEFT_SHIFT, 300))

        if last_action[0] > 0.6:
            pose = "focus" if obs[1] > 0.4 else "attack"
            screen.blit(eleven[pose], (260 + LEFT_SHIFT, 300))

        if obs[4] > 0.5:
            demo_idx = int(obs[5] * 6)
            demo_type = demo_idx % 3
            screen.blit(demo_imgs[demo_type], DEMO_POS[demo_type])
            screen.blit(
                big_font.render(f"Demogorgon {demo_idx + 1} / 6", True, (255,180,180)),
                (760 + LEFT_SHIFT, 220)
            )

        if done and info.get("success"):
            screen.blit(will_img, (860 + LEFT_SHIFT, 300))

    pygame.display.flip()
    clock.tick(60)

    # ==================================================
    # END SCREEN
    # ==================================================
    if done:
        pygame.time.wait(1200)
        screen.fill((0, 0, 0))

        msg = "WILL SAVED" if info.get("success") else "FAILED TO SAVE WILL"
        screen.blit(big_font.render(msg, True, (230,230,230)), (420, 260))
        screen.blit(
            big_font.render(f"Final Combined Power: {info['final_power']:.2f}",
                            True, (200,200,200)),
            (360, 320)
        )

        pygame.display.flip()
        pygame.time.wait(4000)
        running = False

pygame.quit()
