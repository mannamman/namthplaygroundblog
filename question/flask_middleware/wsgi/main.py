from flask import Flask, request, Response
from auth import corsMiddleware, jwtMiddleware
from modify import ModifyMethod, ModifyPostBody

app = Flask('App')

app.wsgi_app = corsMiddleware(app.wsgi_app)
app.wsgi_app = jwtMiddleware(app.wsgi_app)
app.wsgi_app = ModifyMethod(app.wsgi_app)
app.wsgi_app = ModifyPostBody(app.wsgi_app)

@app.route('/', methods=['GET', 'POST'])
def hello():
    msg = request.get_data().decode("utf-8") + "ok"
    return Response(response=msg, status=200)

if __name__ == "__main__":
    app.run(host='localhost', port=5050, debug=True)