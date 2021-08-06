import os
from six.moves import urllib
import json
import base64
import urllib.parse as parse

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

BLOCK_REPLY_V2 ="""
[
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "To quickly help you please select one of the button below and fill out the form with the information"
        }
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Report a Bug",
                    "emoji": true
                },
                "value": "help_me",
                "action_id": "help_me"
            }
        ]
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

BLOCK_MODAL = """
{
	"type": "modal",
	"title": {
		"type": "plain_text",
		"text": "Ansible Helper",
		"emoji": true
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": true
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": true
	},
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Ansible_bug_report",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "ansible_version"
			},
			"label": {
				"type": "plain_text",
				"text": "Ansible Version",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible --version"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "system_version"
			},
			"label": {
				"type": "plain_text",
				"text": "ONTAP / Cloud Manager version",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible --version"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "collection_version"
			},
			"label": {
				"type": "plain_text",
				"text": "Ansible collection version",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible-galaxy collection list"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "problem"
			},
			"label": {
				"type": "plain_text",
				"text": "Description of the problem",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "playbook"
			},
			"label": {
				"type": "plain_text",
				"text": "Playbook",
				"emoji": true
			}
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"multiline": true,
				"action_id": "error"
			},
			"label": {
				"type": "plain_text",
				"text": "Debug output of your playbook",
				"emoji": true
			},
			"hint": {
				"type": "plain_text",
				"text": "ansible-playbook <your playbook> -vvv"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "channel_id:",
				"emoji": true
			}
		},
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "thread_ts:",
				"emoji": true
			}
		}
	]
}
"""

RETURN_TEXT = """
[
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "ansible_version:"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "system_version:"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "collection_version:"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "problem:"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "playbook:"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "error:"
        }
    }
]
"""

action_id = 'help_me'


def send_text_response(event, blocks, channel_id=None, thread_ts=None):
    # use postMessage if we want visible for everybody
    # use postEphemeral if we want just the user to see
    SLACK_URL = "https://slack.com/api/chat.postMessage"
    if not channel_id:
        channel_id = event["event"]["channel"]
    user = None if event == 'NOTHING' else event["event"]["user"]
    bot_token = os.environ["BOT_TOKEN"]
    if not thread_ts:
        thread_ts = event['event']['ts']
    data = urllib.parse.urlencode({
        "token": bot_token,
        "channel": channel_id,
        "blocks": blocks,
        "user": user,
        "link_names": True,
        "parse": True,
        "thread_ts": thread_ts
    })
    data = data.encode("ascii")
    print(data)
    request = urllib.request.Request(SLACK_URL, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    res = urllib.request.urlopen(request).read()
    print('res:', res)

def send_modal(trigger_id, modal):
    slack_url = 'https://slack.com/api/views.open'
    bot_token = os.environ["BOT_TOKEN"]
    data = urllib.parse.urlencode({
        "token": bot_token,
        "trigger_id": trigger_id,
        "view": modal
    })
    data = data.encode("ascii")
    print(data)
    request = urllib.request.Request(slack_url, data=data, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    res = urllib.request.urlopen(request).read()
    print('res:', res)

def parse_button(event):
    print(event)
    # They click a button in the message
    if event['type'] == 'block_actions':
        print(event['actions'][0]['action_id'])
        # Each button has a action_id that we assign to it
        if event['actions'][0]['action_id'] == action_id:
            trigger_id = event['trigger_id']
            channel_id = event['container']['channel_id']
            thread_ts = event['container']['thread_ts']
            modal = update_modal(channel_id, thread_ts)
            send_modal(trigger_id, modal)
    # They clicked the submit button in the modal
    if event['type'] == 'view_submission':
        message, thread_ts, channel_id = parse_responce(event)
        return_block = create_responce_message(message)
        send_text_response('NOTHING', return_block, channel_id, thread_ts)
    return

def parse_responce(event):
    message = {}
    if event['view']['blocks'][0]['text']['text'] == "Ansible_bug_report":
        for block in event['view']['state']['values']:
            for key in event['view']['state']['values'][block]:
                message[key] = event['view']['state']['values'][block][key]['value']
    thread_ts = (event['view']['blocks'][-1]['text']['text']).split(':')[1]
    channel_id = (event['view']['blocks'][-2]['text']['text']).split(':')[1]
    return message, thread_ts, channel_id


def create_responce_message(message):
    return_message = RETURN_TEXT
    print(return_message)
    print('-----')
    for each in message:
        print(each)
        return_message = insert_string(return_message, (each + ':'), (' ' + message[each]))

    print(return_message)
    return return_message

def update_modal(channel_id, thread_ts):
    message = BLOCK_MODAL
    message = insert_string(message, '"text": "channel_id:', channel_id)
    message = insert_string(message, '"text": "thread_ts:', thread_ts)
    return message


def insert_string(message, cut_point, string_to_add):
    index = message.rfind(cut_point)
    cut_point_len = len(cut_point)
    return message[:(index + cut_point_len)] + string_to_add + message[(index + cut_point_len):]

def is_bot(event):
    return 'bot_profile' in event['event']


def lambda_handler(event, context):
    if event["isBase64Encoded"]:
        body = event.get("body", "")
        body = base64.b64decode(body).decode("utf-8")
        # Decoding the base64 return leave all the %22 URL charters, this coverts them to there utf-8 form
        body = parse.unquote(body)
        # Something above cause this to not be valid json, to fix this we just strip the payload= part out, and we get valid json
        body = body.split('payload=')[1]
        event = json.loads(body)
        parse_button(event)

    else:
        event = json.loads(event["body"])
        print('event', event)
        if not is_bot(event) and event["event"]["text"] in REPLYWORDS:
            send_text_response(event, BLOCK_REPLY_V2)

    return {
        'statusCode': 200,
        'body': 'OK'
    }