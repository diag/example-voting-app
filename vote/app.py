from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os,ssl
import socket
import random
import json

option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")
option_c = os.getenv('OPTION_C', "Cows")
hostname = socket.gethostname() 

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
cer = os.path.join(os.path.dirname(__file__), 'tmp/cert.pem')
key = os.path.join(os.path.dirname(__file__), 'tmp/key.pem')
context.load_cert_chain(cer, key)

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis

@app.errorhandler(InvalidUsage)
def handle_bad_request(e):
    return 'bad request!', 400

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        vote = request.form['vote']
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        if vote not in ['a', 'b']:
            raise InvalidUsage('Vote %s is invalid', vote)
        redis.rpush('votes', data)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True, ssl_context=context)
