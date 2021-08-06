import os
from six.moves import urllib
import json

REPLYWORDS = [
    'help',
    'error'
]

BLOCK_REPLY = """
[
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "To quickly help you please reply to this thread with the following information\n• Ansible Version `ansible --version` \n• Collection Version -- `ansible-galaxy collection list`\n"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "If your having issues with a playbook please also include\n• The playbook it self\n• If your getting an error with the playbook the add `-vvv` to the end of the `ansible-playbook` command and copy the output"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "If your requesting a new feature or options\n• For new Features let us know the what the current non ansible command is that you use\n• For new options let us know the Module and which option is missing"
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": ":page_facing_up: <https://docs.ansible.com/ansible/devel/collections/index.html|Ansible Documentation> :page_facing_up: --  :Github: <https://github.com/ansible-collections?q=netapp&type=&language=&sort=| NetApp Github Repos> :Github:"
            }
        ]
    }
]
"""


def send_text_response(event):
    # use postMessage if we want visible for everybody
    # use postEphemeral if we want just the user to see
    SLACK_URL = "https://slack.com/api/chat.postMessage"
    channel_id = event["event"]["channel"]
    user = event["event"]["user"]
    bot_token = os.environ["BOT_TOKEN"]
    thread_ts = event['event']['ts']
    data = urllib.parse.urlencode({
        "token": bot_token,
        "channel": channel_id,
        "blocks": BLOCK_REPLY,
        "user": user,
        "link_names": True,
        "parse": True,
        "thread_ts": thread_ts
    })
    data = data.encode("ascii")
    request = urllib.request.Request(SLACK_URL, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    res = urllib.request.urlopen(request).read()
    print('res:', res)


def is_bot(event):
    return 'bot_profile' in event['event']


def lambda_handler(event, context):
    event = json.loads(event["body"])
    print('event', event)
    if not is_bot(event) and event["event"]["text"] in REPLYWORDS:
        send_text_response(event)

    return {
        'statusCode': 200,
        'body': 'OK'
    }