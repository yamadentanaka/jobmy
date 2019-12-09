import requests
import json
import logging
import traceback
import settings

def send_slack(message, user_name="jobmy_bot", icon_emoji=':robot_face:', channel=None):
    try:
        url = settings.SLACK_WEBHOOK_URL
        if url == "":
            return
        if channel is None:
            channel = settings.SLACK_SEND_CHANNEL
        body = message
        content = body

        payload_dic = {
            "text":content,
            "username": user_name,
            "icon_emoji": icon_emoji,
            "channel": channel,
        }
        # Incoming Webhooksを使って対象のチャンネルにメッセージを送付
        r = requests.post(url, data=json.dumps(payload_dic))
    except Exception as ex:
        logging.error(traceback.format_exc())
