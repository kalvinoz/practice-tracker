"""Constants for the Practice Tracker integration."""

DOMAIN = "practice_tracker"

# Configuration keys
CONF_TRACKER_NAME = "tracker_name"
CONF_NUM_PLAYERS = "num_players"
CONF_PLAYER_NAMES = "player_names"
CONF_TRIGGER_ENTITY = "trigger_entity"

# Defaults
DEFAULT_NAME = "Practice Tracker"
DEFAULT_NUM_PLAYERS = 4
MIN_PLAYERS = 1
MAX_PLAYERS = 8

# Platforms
PLATFORMS = ["select", "sensor"]

# Player options
OPTION_NONE = "None"

# History tracking periods
PERIOD_TODAY = "today"
PERIOD_YESTERDAY = "yesterday"
PERIOD_7_DAYS = "7_days"
PERIOD_28_DAYS = "28_days"

DEFAULT_PERIODS = [PERIOD_TODAY, PERIOD_YESTERDAY, PERIOD_7_DAYS, PERIOD_28_DAYS]
