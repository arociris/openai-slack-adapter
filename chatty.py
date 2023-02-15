import slack
from flask import Flask, jsonify, request
from slackeventsapi import SlackEventAdapter
import openai
import os

# This is slack token

SLACK_TOKEN = os.getenv('SLACK_TOKEN')

SIGNING_SECRET = os.getenv('SIGNING_SECRET')  

# This is openai Key

openai.api_key = os.getenv('AI_API_KEY')


def generate_text(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message


app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)


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
    form = request.form
    channel_id = form.get('channel_id')
    user_id = form.get('user_id')
    text = form.get('text')
    if user_id == "U04P3NK5PC0":
        return

    if text == "hi":
        return "Hello"
    else:
        response = generate_text(text)
        return response
