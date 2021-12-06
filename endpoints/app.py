import json, os, hmac, pytz, hashlib
from os import path
import hashlib
from flask import Flask, request, abort, jsonify
from git import Repo
from changelog import generateHtml, appendToJson
from slack_sdk import WebClient
from flask import Flask, request
from uuid import uuid4
from datetime import datetime
import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

current_dir = path.dirname(path.realpath(__file__))

with open(path.join(current_dir, 'config.json'), 'r') as f:
    config = json.load(f)

app = Flask(__name__)

if "dsn" in config:
    sentry_sdk.init(
        dsn=config["dsn"],
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.0
    )

@app.route('/refresh', methods=['POST'])
def refresh():
    # Updated the website
    header_signature = request.headers.get('X-Hub-Signature')
    if not header_signature:
        abort(403)

    hash_ = header_signature.split('=')[0]
    if hash_ != 'sha1':
        abort(400)

    mac = hmac.new(bytes(config['secret_token'], 'UTF-8'), msg=request.data, digestmod=hashlib.sha1)

    if not hmac.compare_digest(str(mac.hexdigest()), str(header_signature.split('=')[1])):
        abort(403)

    payload = request.get_json()
    if payload['repository']['full_name'] != 'lkellar/website':
        abort(403)

    pull_repo()
    generateHtml()
    return '200 OK', 200

@app.route('/changelog', methods=['POST'])
def update_changelog():
    json_data = request.get_json()
    if 'post' not in json_data:
        return jsonify({'error': 'Post not included in request'}), 400

    if 'title' not in json_data:
        return jsonify({'error': 'Title not included in request'}), 400

    if 'key' not in json_data:
        return jsonify({'error': 'No Key Provided!'}), 401

    h = hashlib.sha256()
    h.update(json_data['key'].encode('utf-8'))

    if h.hexdigest() != config['changelog_token']:
        return jsonify({'error': 'Unauthorized'}), 401

    pull_repo()

    if 'seperator' in json_data:
        post = json_data['post'].split(json_data['seperator'])
    else:
        post = json_data['post']

    appendToJson(json_data['title'], post)

    generateHtml()

    return '200 OK'

def pull_repo():
    repo = Repo(path.join(current_dir, '../'))
    assert not repo.bare
    o = repo.remotes.origin
    o.pull()
    

@app.route('/slack-update', methods=['POST'])
def updateStatus():
    if 'secret_token' not in config:
        return 'No Scrape Key in config.json 🤷', 501

    if request.form.get('secret_token') != config['secret_token']:
        return 'Incorrect/Missing Scrape Key', 401
    
    with open(path.join(current_dir, 'schedule.json'), 'r') as f:
        data = json.load(f)
        
    with open(path.join(current_dir, 'tokens.json'), 'r') as f:
        tokens = json.load(f)
    
    if 'user_token' not in tokens:
        return 'User token not found. Please install slack bot', 401   
    
    today = datetime.now(pytz.timezone("America/Chicago")).strftime("%Y-%m-%d")
    expiry_time = datetime.now(pytz.timezone("America/Chicago")).replace(hour=17, minute=00, second=0).timestamp()
    
    if today in data:
        client = WebClient(token=tokens['user_token'])
        client.users_profile_set(status_text="School", status_emoji=":school:", status_expiration=expiry_time)

    return "Status not adjusted", 200

client_id = config["SLACK_CLIENT_ID"]
client_secret = config["SLACK_CLIENT_SECRET"]
oauth_scope = config["SLACK_SCOPES"]
    
@app.route("/slack/install", methods=["GET"])
def pre_install():
    state = str(uuid4())
    return '<a href="https://slack.com/oauth/v2/authorize?' \
        f'user_scope={oauth_scope}&client_id={client_id}&state={state}&redirect_uri=https://lkellar.org/endpoints/slack/oauth_redirect">' \
        'Add to Slack</a>'
        
@app.route("/slack/oauth_redirect", methods=["GET"])
def post_install():
    if path.exists(path.join(current_dir, 'tokens.json')):
        return 'Someone already authd', 400
    # Verify the "state" parameter

    # Retrieve the auth code from the request params
    code_param = request.args['code']

    # An empty string is a valid token for this request
    client = WebClient()

    # Request the auth tokens from Slack
    response = client.oauth_v2_access(
        client_id=client_id,
        client_secret=client_secret,
        code=code_param
    )
    # Save the bot token to an environmental variable or to your data store
    # for later use
    tokens = {
        "scope": response['authed_user']['scope'],
        "token_type": response['authed_user']['token_type'],
        "user_token": response['authed_user']['access_token']
    }
     
    with open(path.join(current_dir, 'tokens.json'), 'w') as f:
        json.dump(tokens, f)

    # Don't forget to let the user know that OAuth has succeeded!
    return "Installation is completed!"

if __name__ == "__main__":
    app.run()
