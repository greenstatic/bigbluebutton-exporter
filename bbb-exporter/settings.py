import os
import api_lib

MAJOR = 0
MINOR = 2
BUGFIX = 0

VERSION = "{}.{}.{}".format(MAJOR, MINOR, BUGFIX)

debug_env = os.getenv("DEBUG", "false")
DEBUG = True if debug_env.lower() == "true" else False

API_BASE_URL = os.environ["API_BASE_URL"]
# SSH into server and run: `$ bbb-conf --secret` to get secret
API_SECRET = os.environ["API_SECRET"]

API_CLIENT = api_lib.Client(API_BASE_URL, API_SECRET)

PORT = int(os.getenv("PORT", 9688))


# Global (gasp.) variable flag that is used to mark if communicating with BigBlueButton's API is possible.
# Used to set the `bbb_api_up` metric.
_api_up = False
