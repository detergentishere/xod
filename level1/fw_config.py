# fw_config.py

# -------- Environment limits --------
MAX_STEPS = 25

# -------- Scoring --------
STEP_PENALTY = -1
CLUE_REWARD = 5
BELIEF_REWARD = 2

SUCCESS_REWARD = 500
FAILURE_PENALTY = -200

# -------- State bounds --------
MAX_SIGNAL = 10
MAX_FATIGUE = 10
MAX_STRESS = 10
MAX_LAB_ATTENTION = 10

# -------- Actions --------
USE_ELEVENS_POWER = 0
SEARCH_LAB = 1
ENTER_UPSIDE_DOWN = 2
READ_LIGHTS = 3
SPLIT_TEAM = 4
SET_BAIT = 5

ACTION_NAMES = {
    0: "USE_ELEVENS_POWER",
    1: "SEARCH_LAB",
    2: "ENTER_UPSIDE_DOWN",
    3: "READ_LIGHTS",
    4: "SPLIT_TEAM",
    5: "SET_BAIT"
}
