import logging
from fastapi import FastAPI, Request

from alert_manager import handle_alerts
from initialize import MESSENGER_URL, WORKSPACEID, CHATID

app = FastAPI()
logger = logging.getLogger(__name__)


@app.post("/")
async def manage_route(request: Request):
    try:
        data = await request.json()
        url_MESSENGER_chat = (
            f"{MESSENGER_URL}botapi/v1/messages/sendTextMessage/{WORKSPACEID}/{CHATID}"
        )
        handle_alerts(WORKSPACEID, CHATID, data, url_MESSENGER_chat)
        return {"status_code": 200}
    except Exception as e:
        logger.critical("An unexpected error occurred: %s", e)
        return {"status_code": 500}
