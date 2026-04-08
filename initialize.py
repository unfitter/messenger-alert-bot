import logging
import os
import sys
from http.client import HTTPException

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.getenv("LOGLEVEL", "INFO").upper()))
logger.addHandler(logging.StreamHandler(sys.stdout))

TOKEN_MESSENGER = os.getenv("TOKEN_MESSENGER", None)
MESSENGER_URL = os.getenv("MESSENGER_URL", None)
# GENERAL_NUMBER = os.getenv("GENERAL_NUMBER", None)
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM", None)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", None)

# These are defined in the Kubernetes Deployment env (exact names)
WORKSPACEID = os.getenv("WORKSPACEID", None)
CHATID = os.getenv("CHATID", None)

# JIRA_USABILITY = 'true' or 'false'

url_MESSENGER_call = f"{MESSENGER_URL}botapi/v1/vcs/startCall"


def _require_env(name: str, value: str | None) -> None:
    if value is None or str(value).strip() == "":
        logger.critical("%s not found in environment variables!", name)
        raise HTTPException(status_code=500, detail=f"{name} not found.")


# Required envs
_require_env("TOKEN_MESSENGER", TOKEN_MESSENGER)
_require_env("MESSENGER_URL", MESSENGER_URL)
_require_env("WORKSPACEID", WORKSPACEID)
_require_env("CHATID", CHATID)

# Normalize types for downstream use
WORKSPACEID = int(WORKSPACEID)
CHATID = int(CHATID)

# Optional: duty group envs. If not set, default to main WORKSPACEID/CHATID
DUTY_WORKSPACE = os.getenv("DUTY_WORKSPACE", str(WORKSPACEID))
DUTY_CHAT = os.getenv("DUTY_CHAT", str(CHATID))
_require_env("DUTY_WORKSPACE", DUTY_WORKSPACE)
_require_env("DUTY_CHAT", DUTY_CHAT)
DUTY_WORKSPACE = int(DUTY_WORKSPACE)
DUTY_CHAT = int(DUTY_CHAT)