from werkzeug.wrappers import Request, Response, ResponseStream
import jwt

class corsMiddleware():
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        if(request.method == "GET"):
            res = Response(status=200, response="pong", mimetype= "text/plain")
            return res(environ, start_response)
        elif(request.method == 'OPTIONS'):
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': ["GET","POST"],
                'Access-Control-Allow-Headers': ['Content-Type', 'Authorization'],
                'Access-Control-Max-Age': '3600'
            }
            res = Response(status=204, response="", headers=headers, mimetype= "text/plain")
            return res(environ, start_response)
        
        return self.app(environ, start_response)


class jwtMiddleware():
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        if("Authorization" not in request.headers):
            res = Response(status=401, response="Authorization is not exist", headers=headers)
            return res(environ, start_response)
        jwt_header = request.headers["Authorization"]
        try:
            token_type, token = jwt_header.split(" ")
            if(token_type.lower() != "bearer"):
                raise ValueError
            secret = 'thsissecret'
            jwt.decode(token, secret, algorithms=["HS256"])
        except Exception as e:
            res = Response(status=400, response="Authorization Failed", headers=headers)
            return res(environ, start_response)

        return self.app(environ, start_response)
