import os
import api_lib

MAJOR = 0
MINOR = 1
BUGFIX = 2

VERSION = "{}.{}.{}".format(MAJOR, MINOR, BUGFIX)

debug_env = os.getenv("DEBUG", "false")
DEBUG = True if debug_env.lower() == "true" else False

API_BASE_URL = os.environ["API_BASE_URL"]
# SSH into server and run: `$ bbb-conf --secret` to get secret
API_SECRET = os.environ["API_SECRET"]

API_CLIENT = api_lib.Client(API_BASE_URL, API_SECRET)

PORT = int(os.getenv("PORT", 9688))

# Sleep duration for BBB API polling
SLEEP_DURATION = int(os.getenv("SLEEP_DURATION", 5))  # seconds
