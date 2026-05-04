import json, os, hmac, hashlib
from os import path, mkdir
from flask import Flask, request, abort, redirect
from git import Repo
from datetime import datetime, timedelta
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import pathlib
import random
from markupsafe import escape
from werkzeug.utils import secure_filename
import shutil
import pytz

current_dir = path.dirname(path.realpath(__file__))

with open(path.join(current_dir, 'config.json'), 'r') as f:
    config = json.load(f)

app = Flask(__name__)

# while the server is in Fayetteville, the displayed time will also be in Fayetteville time
tz = pytz.timezone('America/Chicago')

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
    dewey_path = pathlib.Path(config['dewey_path'])
    pics = list(dewey_path.glob('*.jpg'))
    name = random.choice(pics).name
    
    return redirect(f'/dewey/noon/{name}', code=302)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def clear_whats_new():
    dir = path.join(current_dir, '../whats_new/')
    if path.isdir(dir):
        shutil.rmtree(dir)
    
    mkdir(dir)

@app.route('/clear_whats_new', methods=['POST'])
def clear_whats_new_route():
    if 'secret_key' not in request.form:
        return 'Missing key', 401
    
    if config['whats_new_token'] != request.form['secret_key']:
        return 'Invalid key', 401
    clear_whats_new()
    return 'OK', 200

# update the what's new thing
@app.route('/whats_new', methods=['POST'])
def whats_new():
    if 'secret_key' not in request.form:
        return 'Missing key', 401
    
    if config['whats_new_token'] != request.form['secret_key']:
        return 'Invalid key', 401
    
    clear_whats_new()
    html = f'''<div class="whats_new">
    <h3>What's New</h3>'''
    if 'image' in request.files:
        image = request.files['image']
        
        filename = image.filename
        if '.' in filename and filename.split('.')[-1] in ALLOWED_EXTENSIONS:
            ext = filename.split('.')[-1]
            # just in case
            name = secure_filename(f'image.{ext}')
            filepath = path.join(current_dir, '../whats_new/', name)
            image.save(filepath)
            html += f'\n<img src="{name}" />'
    
    if 'text' in request.form and len(request.form['text']) > 0:
        html += f'\n<p>{escape(request.form['text'])}</p>'
    
    arkansas_now = datetime.now(tz)
    timestamp = arkansas_now.strftime('%m/%d/%Y %H:%M:%S')
    html += f'<p class="timestamp">{timestamp} Arkansas Time</p>'
    html += "\n</div>"
    with open(path.join(current_dir, '../whats_new/index.html'), 'w') as f:
        f.write(html)
    
    # default time week
    expiry_time = datetime.now() + timedelta(days=7)
    if 'expiry_days' in request.form and request.form['expiry_days'].isdigit():
        try:
            days = int(request.form['expiry_days'])
            expiry_time = datetime.now() + timedelta(days=days)
        except ValueError:
            pass
    
    with open(path.join(current_dir, '../whats_new/expiry.txt'), 'w') as f:
        f.write(str(int(expiry_time.timestamp())))
        
    return 'OK', 200

if __name__ == "__main__":
    app.run()
