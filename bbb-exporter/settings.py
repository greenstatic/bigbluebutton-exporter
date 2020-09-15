import os
import api_lib
from helpers import validate_api_base_url, validate_buckets, str_to_bool_or_none

MAJOR = 0
MINOR = 5
BUGFIX = 2
INFO = ""

VERSION = "{}.{}.{}".format(MAJOR, MINOR, BUGFIX)
if INFO:
    VERSION += "-" + INFO

debug_env = os.getenv("DEBUG", "false")
DEBUG = True if debug_env.lower() == "true" else False

tls_verify_temp = os.getenv("TLS_VERIFY", "true")

TLS_VERIFY = str_to_bool_or_none(tls_verify_temp)
if TLS_VERIFY is None:
    # If we failed to determine a boolean value it means it (should) be a string representing the CA_BUNDLE path
    TLS_VERIFY = tls_verify_temp

API_BASE_URL = validate_api_base_url(os.environ["API_BASE_URL"])
# SSH into server and run: `$ bbb-conf --secret` to get secret
API_SECRET = os.environ["API_SECRET"]

API_CLIENT = api_lib.Client(API_BASE_URL, API_SECRET, TLS_VERIFY)

ROOM_PARTICIPANTS_CUSTOM_BUCKETS = validate_buckets(os.getenv("ROOM_PARTICIPANTS_CUSTOM_BUCKETS", default=""))
ROOM_LISTENERS_CUSTOM_BUCKETS = validate_buckets(os.getenv("ROOM_LISTENERS_CUSTOM_BUCKETS", default=""))
ROOM_VOICE_PARTICIPANTS_CUSTOM_BUCKETS = validate_buckets(
    os.getenv("ROOM_VOICE_PARTICIPANTS_CUSTOM_BUCKETS", default=""))
ROOM_VIDEO_PARTICIPANTS_CUSTOM_BUCKETS = validate_buckets(
    os.getenv("ROOM_VIDEO_PARTICIPANTS_CUSTOM_BUCKETS", default=""))

PORT = int(os.getenv("PORT", 9688))
BIND_IP = os.getenv("BIND_IP", "0.0.0.0")

RECORDINGS_METRICS_ENABLE = False if os.getenv("RECORDINGS_METRICS", "true").lower() == "false" else True

RECORDINGS_METRICS_READ_FROM_DISK = False if os.getenv("RECORDINGS_METRICS_READ_FROM_DISK",
                                                       "false").lower() == "false" else True
recordings_metrics_base_dir = "/var/bigbluebutton"

# Global (gasp.) variable flag that is used to mark if communicating with BigBlueButton's API is possible.
# Used to set the `bbb_api_up` metric.
_api_up = False
