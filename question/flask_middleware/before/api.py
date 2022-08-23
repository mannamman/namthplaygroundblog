from flask import Blueprint, Response
from auth import health_cors, jwt_deco

def make_api():
    api = Blueprint("test", __name__)

    api.before_request(health_cors)
    api.before_request(jwt_deco)

    @api.route('/foo', methods=['GET', 'POST'])
    def ping():
        return Response(response="pong", status=200)
    
    return api
