import json
import requests
import slack
from flask import Flask, jsonify, request
from slackeventsapi import SlackEventAdapter
import openai
import os
import threading
import logging

# This is slack token

SLACK_TOKEN = os.getenv('SLACK_TOKEN')

SIGNING_SECRET = os.getenv('SIGNING_SECRET')

# This is openai Key

openai.api_key = os.getenv('AI_API_KEY')

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)


def generate_text(prompt):
    completions = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message


def process_slash_command(form_data):
    try:
        channel_id = form_data['channel_id']
        text = form_data['text']
        user_id = form_data['user_id']
        response_url = form_data['response_url']
        response = generate_text(text)
        # Check if command was invoked in a channel or a DM
        if channel_id.startswith('D'):
            requests.post(response_url, data=json.dumps({"text": response}))
        else:
            client.chat_postMessage(channel=channel_id, text=response)

    except Exception as e:
        logging.exception("Error processing slash command: %s", str(e))


@slack_event_adapter.on('message')
def message(payload):
    print(payload)

    event = payload.get('event', {})
    if "client_msg_id" in event and "event_subtype" not in event and "bot_id" not in event:
        channel_id = event.get('channel')
        user_id = event.get('user')
        text = event.get('text')
        if user_id == "U04P3NK5PC0":
            return 200

        if text == "hi":
            client.chat_postMessage(channel=channel_id, text="Hello")
            return 200
        else:
            response = generate_text(text)
            client.chat_postMessage(channel=channel_id, text=response)
            return 200


@app.route('/slack/chatty', methods=['POST'])
def chatty():
    print(request.form);
    form = dict(request.form)
    user_id = form.get('user_id')
    text = form.get('text')
    if user_id == "U04P3NK5PC0":
        return

    if text == "hi":
        return "Hello"
    else:
        thread = threading.Thread(target=process_slash_command, args=(form,))
        thread.start()
        return ''


if __name__ == "__main__":
    app.run(debug=True)
