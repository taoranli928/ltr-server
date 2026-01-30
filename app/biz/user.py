from datetime import datetime
import flask
from . import token


def check_password(password):
    today = datetime.now().strftime("%m%d")
    return password == today


def login(login_request: dict):
    username = login_request['username']
    password = login_request['password']
    if not check_password(password):
        return {}

    token_payload = {
        "username": username
    }
    jwt_token = token.generate_jwt_token(token_payload, 6*60)
    return {
        "username": username,
        "token": jwt_token
    }


def check_token():
    token_from_cookie = flask.request.cookies.get('token')
    if not token_from_cookie:
        return None
    payload = token.verify_jwt_token(token_from_cookie)
    if not payload:
        return None
    return payload['username']
