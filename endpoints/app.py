import json
import hmac
from os import path, environ
from datetime import datetime
import hashlib
from flask import Flask, request, abort, jsonify
from git import Repo
from changelog import generateHtml, appendToJson

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

    hash_ = header_signature.split('=')[0]
    if hash_ != 'sha1':
        abort(400)

    mac = hmac.new(bytes(config['secret_token'], 'UTF-8'), msg=request.data, digestmod=hashlib.sha1)

    if not hmac.compare_digest(str(mac.hexdigest()), str(header_signature.split('=')[1])):
        abort(403)

    payload = request.get_json()
    if payload['repository']['full_name'] != 'katzrkool/website':
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

    if h.hexdigest() != environ['WEBSITE_CHANGELOG_HEX']:
        return jsonify({'error': 'Unauthorized'}), 401

    pull_repo()

    repo = Repo(path.join(current_dir, '../'))

    appendToJson(json_data['title'], json_data['post'])

    repo.git.add(path.join(path.dirname(path.realpath(__file__)), '../', 'changelog/storage.json'))

    repo.index.commit(f'Updated changelog: {datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")}')

    with repo.git.custom_environment(GIT_SSH_COMMAND=environ['ssh_cmd']):
        repo.remotes.origin.push()

    return '200 OK'

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

    if h.hexdigest() != environ['WEBSITE_CHANGELOG_HEX']:
        return jsonify({'error': 'Unauthorized'}), 401

    pull_repo()

    appendToJson(json_data['title'], json_data['post'])

    generateHtml()

    return '200 OK'

def pull_repo():
    repo = Repo(path.join(current_dir, '../'))
    assert not repo.bare
    o = repo.remotes.origin
    o.pull()


if __name__ == "__main__":
    app.run()
