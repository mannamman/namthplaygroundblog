from flask import Flask, request, Response
import functools
from auth import health_cors, jwt_deco

app = Flask('App')

def abstract_request(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(request)
    return wrapper

@app.route('/', methods=['GET', 'POST'])
@abstract_request
@health_cors
@jwt_deco
def ping():
    return Response(response="pong", status=200)

if __name__ == "__main__":
    app.run('127.0.0.1', '5000', debug=True)