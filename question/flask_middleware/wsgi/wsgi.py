from flask import Flask, request, Response
from auth import jwtMiddleware, corsMiddleware

app = Flask('App')

app.wsgi_app = corsMiddleware(app.wsgi_app)
app.wsgi_app = jwtMiddleware(app.wsgi_app)

@app.route('/', methods=['GET', 'POST'])
def hello():
    return Response(response="ok", status=200)

if __name__ == "__main__":
    app.run('127.0.0.1', '5000', debug=True)