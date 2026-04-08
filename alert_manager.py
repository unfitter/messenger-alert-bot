# flake8: noqa
# pylint: disable=E1120,W0611
import logging
from jinja2 import Environment, FileSystemLoader
from requests.exceptions import HTTPError
import requests
import time
import json

from initialize import TOKEN_MESSENGER, TOKEN_TELEGRAM, TELEGRAM_CHAT_ID
from call_center import check_info_for_call

logger = logging.getLogger(__name__)


def handle_alerts(workspace_id, chat_id, data, url_MESSENGER_chat):
    firing = len(list(filter(lambda x: x.get('status') == "firing", data.get('alerts'))))
    resolved = len(list(filter(lambda x: x.get('status') == 'resolved', data.get('alerts'))))
    critical_alerts = False
    if isinstance(data.get('alerts'), list):
        for alert in data['alerts']:

            if alert.get('labels', {}).get('severity', None) == 'critical':
                critical_alerts = True
        if critical_alerts:
            check_info_for_call()
    create_template(data, firing, resolved, workspace_id, chat_id, url_MESSENGER_chat)


def create_template(data, firing, resolved, workspace_id, chat_id, url_MESSENGER_chat):
    try:
        env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True,
                          lstrip_blocks=True)
        template = env.get_template('alert-message.j2')
        alert = str(template.render({'data': data,
                                     'firing': firing,
                                     'resolved': resolved}))
        logger.critical('type of alert var: %s', type(alert))
        message = {'clientRandomId': int(time.time()), 'message': alert}
        send_alerts(workspace_id, chat_id, data, url_MESSENGER_chat, message)
        return None
    except ValueError:
        logger.critical("Value error! Bad data from alertmanager", ValueError)
        return {"status_code": 400}
    except FileNotFoundError:
        logger.critical("Alert-message template not found!")
        return {"status_code": 400}


def send_alerts(workspace_id, chat_id, data, url_MESSENGER_chat, message):
    max_attempts = 5
    attempt = 0
    success = False
    while attempt < max_attempts and not success:
        attempt += 1
        try:
            response_text = requests.post(
                url_MESSENGER_chat,
                data=json.dumps(message),
                timeout=2,
                headers={'Authorization': TOKEN_MESSENGER, 'Content-Type': 'application/json'})
            response_text.raise_for_status()
            logger.info("Alert sent successfully, status code: %s",
                        response_text.status_code)
            success = True
            return {"status_code": response_text.status_code}
        except HTTPError:
            logger.critical("Error while try send alerts in chat - %s, %s\nreason: %s (%s)\n",
                            workspace_id, chat_id, response_text.text, response_text.status_code)
        time.sleep(5)
    if not success:
        reserve_alerting(message['message'])
    return {"status_code": response_text.status_code if 'response_text' in locals() else 500}


def reserve_alerting(message):
    try:
        tg_url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        tg_data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        tg_resp = requests.post(tg_url, data=tg_data, timeout=5)
        tg_resp.raise_for_status()
        logger.info("Alert duplicated to Telegram, status code: %s", tg_resp.status_code)
    except Exception as e:
        logger.critical("Failed to duplicate alert to Telegram: %s", e)
