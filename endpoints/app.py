import json, os, hmac, hashlib
from os import path
from flask import Flask, request, abort, redirect
from git import Repo
from datetime import datetime, timedelta
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import pathlib
import random

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
    return '200 OK', 200

def pull_repo():
    repo = Repo(path.join(current_dir, '../'))
    assert not repo.bare
    o = repo.remotes.origin
    o.pull()
    
# return a redirect to a random dewey
@app.route('/random_dewey', methods=['GET'])
def random_dewey():
    path = pathlib.Path(config['dewey_path'])
    pics = list(path.glob('*.jpg'))
    name = random.choice(pics).name
    
    return redirect(f'/dewey/noon/{name}', code=302)
    

if __name__ == "__main__":
    app.run()
