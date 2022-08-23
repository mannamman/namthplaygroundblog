from flask import Response, request
import jwt


def health_cors():
    if(request.method == "GET"):
        return Response(status=200, response="pong")
    elif(request.method == 'OPTIONS'):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': ["GET","POST"],
            'Access-Control-Allow-Headers': ['Content-Type', 'Authorization'],
            'Access-Control-Max-Age': '3600'
        }
        return Response(status=204, response="", headers=headers)

def jwt_deco():
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    if("Authorization" not in request.headers):
        return Response(status=401, response="Authorization is not exist", headers=headers)
    jwt_header = request.headers["Authorization"]
    try:
        token_type, token = jwt_header.split(" ")
        if(token_type.lower() != "bearer"):
            raise ValueError
        secret = 'thsissecret'
        jwt.decode(token, secret, algorithms=["HS256"])
    except Exception as e:
        return Response(status=400, response="Authorization Failed", headers=headers)
