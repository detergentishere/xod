# train_loop.py
from finding_will_env import FindWillEnv
from agent import StrategicAgent

EPISODES = 400
VIS_INTERVAL = 100

best_score = -1e9
best_trajectory = None

agent = StrategicAgent()

all_episode_paths = []

for ep in range(1, EPISODES + 1):
    env = FindWillEnv()
    obs, _ = env.reset()

    done = False
    trajectory = []

    while not done:
        action = agent.act(obs)
        next_obs, reward, done, _, info = env.step(action)
        trajectory.append((obs, action))
        obs = next_obs

    success = info["success"]
    final_score = info["final_power"]


    # Store best episode
    if success and final_score > best_score:
        best_score = final_score
        best_trajectory = trajectory

    all_episode_paths.append((trajectory, final_score, success))

    print(f"Episode {ep:03d} | Success={success} | Final={final_score:.2f}")

    # Save episodes to visualize later
    if ep % VIS_INTERVAL == 0:
        with open(f"replay_ep_{ep}.pkl", "wb") as f:
            import pickle
            pickle.dump(trajectory, f)

# Save best path
with open("best_path.pkl", "wb") as f:
    import pickle
    pickle.dump(best_trajectory, f)

print(f"\nBest final power: {best_score:.2f}")
