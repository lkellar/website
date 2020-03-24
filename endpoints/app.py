import json
import hmac
from os import path
from flask import Flask, request, abort
from git import Repo

current_dir = path.dirname(path.realpath(__file__))

with open(path.join(current_dir, 'config.json'), 'r') as f:
    config = json.load(f)

app = Flask(__name__)

@app.route('/refresh', methods=['POST'])
def refresh():
    # Updated the website
    header_signature = request.headers.get('X-Hub-Signature')
    if not header_signature:
        abort(403)

    hash_ = header_signature.split('=')
    if hash_ != 'sha1':
        abort(400)

    mac = hmac.new(str(config['secret']), msg=request.data, digestmod='sha1')

    if str(mac.hexdigest) != str(header_signature.split('=')[1]):
        print('Signatures do not match')
        abort(403)

    payload = request.get_json()
    if payload['respository']['full_name'] != 'katzrkool/website':
        abort(403)

    update_website()
    return '200 OK', 200

def update_website():
    repo = Repo(path.join(current_dir, '../'))
    assert not repo.bare
    o = repo.remotes.origin
    o.pull()

if __name__ == "__main__":
    app.run()
