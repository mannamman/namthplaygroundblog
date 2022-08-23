import functools
from flask import Response, Request
import os
import jwt


def health_cors(func):
    @functools.wraps(func)
    def wrapper(req: Request):
        if(req.method == "GET"):
            return Response(status=200, response="pong")
        elif(req.method == 'OPTIONS'):
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': ["GET","POST"],
                'Access-Control-Allow-Headers': ['Content-Type', 'Authorization'],
                'Access-Control-Max-Age': '3600'
            }
            return Response(status=204, response="", headers=headers)
        return func(req)
    return wrapper


def jwt_deco(func):
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    @functools.wraps(func)
    def valid(req: Request):
        if("Authorization" not in req.headers):
            return Response(status=401, response="Authorization is not exist", headers=headers)
        jwt_header = req.headers["Authorization"]
        try:
            token_type, token = jwt_header.split(" ")
            if(token_type.lower() != "bearer"):
                raise ValueError
            secret = 'thsissecret'
            jwt.decode(token, secret, algorithms=["HS256"])
        except Exception as e:
            return Response(status=400, response="Authorization Failed", headers=headers)
        return func(req)
    return valid