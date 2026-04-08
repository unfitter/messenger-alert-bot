# pylint: disable=C0414,R1710
import json
import logging
from time import sleep
from urllib.error import HTTPError
import requests as requests
from initialize import TOKEN_MESSENGER, MESSENGER_URL, DUTY_WORKSPACE, DUTY_CHAT

logger = logging.getLogger(__name__)


def check_info_for_call():
    data = get_users_from_group()
    for user in (data or []):
        if not user['bot']:
            make_call(user['userId'])
        else:
            logger.warning('Assignee not found in the group')
        sleep(30)


def make_call(on_duty):
    try:
        headers = {
            'Authorization': TOKEN_MESSENGER,
            'WorkspaceId': '-1', 'Content-Type': 'application/json'}
        body = {"userId": on_duty, "userPhone": None}
        response_call = requests.post(url=f'{MESSENGER_URL}botapi/v1/vcs/startCall', headers=headers, timeout=2,
                                      data=json.dumps(body))
        response_call.raise_for_status()
        logger.info("Call assignee: %s, %s", on_duty, response_call.status_code)
        return {"status_code": response_call.status_code}
    except HTTPError:
        logger.critical("Error while try to call in chat ! %s", HTTPError)
        return {"status_code": response_call.status_code if 'response_call' in locals() else 503}


def get_users_from_group():
    try:
        headers = {
            'Authorization': TOKEN_MESSENGER,
            'Content-Type': 'application/json'}
        response = requests.get(
            url=f'{MESSENGER_URL}botapi/v1/groups/getUsersGroup/{DUTY_WORKSPACE}/group/{DUTY_CHAT}',
            headers=headers, timeout=2)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error("HTTP error occurred: %s", http_err)
        try:
            logger.error("Response code: %s", response.status_code)
            logger.error("Response text: %s", response.text)
        except Exception:
            pass
        return []
    except Exception as err:
        logger.error("Unexpected error in get_users_from_group: %s", err)
        return []