# run_visual.py
import pygame
import math
from finding_will_env import FindingWillEnv, MAX_MOVES, World
from agent import ExploratoryAgent

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 560
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Finding Will")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)

# -------- Timing --------
STEP_DELAY_MS = 500
last_step_time = 0

# -------- Heartbeat --------
heartbeat_phase = 0.0
last_heartbeat = 0

# -------- Assets --------
bg_home = pygame.transform.scale(pygame.image.load("assets/home.jpg"), (WIDTH, HEIGHT))
bg_lab = pygame.transform.scale(pygame.image.load("assets/lab_bg.jpg"), (WIDTH, HEIGHT))
bg_upside = pygame.transform.scale(pygame.image.load("assets/upside_down.jpg"), (WIDTH, HEIGHT))

eleven_img = pygame.transform.scale(pygame.image.load("assets/eleven.png"), (120, 180))
demogorgon_img = pygame.transform.scale(pygame.image.load("assets/demogorgan.png"), (160, 220))
will_img = pygame.transform.scale(pygame.image.load("assets/will.png"), (120, 180))
light_img = pygame.transform.scale(pygame.image.load("assets/lights.webp"), (18, 18))

heartbeat_sound = pygame.mixer.Sound("assets/heartbeat.mp3")
step_sound = pygame.mixer.Sound("assets/step.mp3")
heartbeat_sound.set_volume(0.35)
step_sound.set_volume(0.2)

env = FindingWillEnv()
agent = ExploratoryAgent()
obs, _ = env.reset()

done = False
running = True
final_info = {}

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------- Timed Step --------
    if not done and current_time - last_step_time > STEP_DELAY_MS:
        obs, _, done, _, final_info = env.step(agent.act(obs))
        step_sound.play()
        last_step_time = current_time

    # -------- Background --------
    if env.world == World.HOME:
        screen.blit(bg_home, (0, 0))
    elif env.world == World.LAB:
        screen.blit(bg_lab, (0, 0))
    else:
        screen.blit(bg_upside, (0, 0))

    # -------- Lights --------
    if env.lights.used:
        for i in range(18):
            x = 120 + i * 45
            y = 40 + math.sin(env.lights.phase + i * 0.6) * 8
            screen.blit(light_img, (x, int(y)))

    # -------- Characters --------
    if env.eleven.used and env.world == World.LAB:
        screen.blit(eleven_img, (80, 300))

    if env.demogorgon.visible and env.world == World.UPSIDE_DOWN:
        screen.blit(demogorgon_img, (740, 260))

    if final_info.get("success"):
        screen.blit(will_img, (520, 300))

    # -------- Heartbeat Visual + Sound --------
    heartbeat_phase += 0.04 + env.stress * 0.08
    pulse = (math.sin(heartbeat_phase) + 1) * 0.5

    if env.stress > 0.4:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(int(40 * env.stress * pulse))
        screen.blit(overlay, (0, 0))

        interval = int(1200 - env.stress * 700)
        if current_time - last_heartbeat > interval:
            heartbeat_sound.play()
            last_heartbeat = current_time

    # -------- HUD --------
    pygame.draw.rect(screen, (15, 15, 25), (0, 0, WIDTH, 50))
    screen.blit(font.render(f"Belief: {env.belief:.2f}", True, (220, 220, 220)), (20, 14))
    screen.blit(font.render(f"Stress: {env.stress:.2f}", True, (220, 220, 220)), (220, 14))
    screen.blit(
        font.render(f"Moves: {env.moves_left}/{MAX_MOVES}", True, (220, 220, 220)),
        (420, 14)
    )

    pygame.display.flip()
    clock.tick(60)

    # -------- End --------
    if done:
        pygame.time.wait(800)
        screen.fill((0, 0, 0))
        msg = "WILL FOUND" if final_info.get("success") else "FAILED TO FIND WILL"
        text = font.render(msg, True, (230, 230, 230))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

pygame.quit()
