import flask
import threading
from biz import user, room

app = flask.Flask(__name__)

global_lock = threading.Lock()


@app.route('/')
def hello():
    return "Hello from ltr-server!"


@app.route('/index')
def index_page():
    return flask.render_template('index.html')


@app.route('/login')
def login_page():
    return flask.render_template('login.html')


@app.route('/lobby')
def lobby_page():
    return flask.render_template('lobby.html')


@app.route('/room')
def room_page():
    return flask.render_template('room.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    body = flask.request.json
    result = user.login(body)
    if not result:
        return flask.jsonify({
            "success": False,
            "msg": "密码错误～"
        })

    username = result['username']
    token = result['token']

    response = flask.jsonify({
        "success": True,
        "username": username,
    })

    response.set_cookie(
        key='token',
        value=token,
        max_age=6 * 60 * 60,
        httponly=False,
        secure=False,
        path='/'
    )

    response.set_cookie(
        key='user',
        value=username,
        max_age=6 * 60 * 60,
        httponly=False,
        secure=False,
        path='/'
    )
    return response


@app.route('/api/login/check', methods=['GET'])
def api_login_check():
    username = user.check_token()
    return flask.jsonify({
        "success": True,
        "reLogin": username is None,
        "username": username,
    })


@app.route('/api/room/create', methods=['GET'])
def create_room():
    with global_lock:
        username = user.check_token()
        if not username:
            return flask.jsonify({
                "success": True,
                "reLogin": True,
            })

        room_id = room.create_room(username)
        return flask.jsonify({
            "success": True,
            "roomId": room_id,
        })


@app.route('/api/room/join', methods=['POST'])
def join_room():
    with global_lock:
        username = user.check_token()
        if not username:
            return flask.jsonify({
                "success": True,
                "reLogin": True,
            })

        request_room_id = flask.request.json['roomId']
        exist, room_id = room.join_room(username, request_room_id)
        if not exist:
            return flask.jsonify({
                "success": False,
                "msg": "房间不存在：" + request_room_id,
            })

        return flask.jsonify({
            "success": True,
            "roomId": room_id,
        })


@app.route('/api/room/list', methods=['GET'])
def list_room():
    username = user.check_token()
    if not username:
        return flask.jsonify({
            "success": True,
            "reLogin": True,
        })

    room_list = room.list_room(username)
    return flask.jsonify({
        "success": True,
        "rooms": room_list,
    })


@app.route('/api/room/detail', methods=['POST'])
def get_room_detail():
    username = user.check_token()
    if not username:
        return flask.jsonify({
            "success": True,
            "reLogin": True,
        })

    room_id = flask.request.json['roomId']
    room_detail, room_summary = room.room_detail(room_id)
    return flask.jsonify({
        "success": True,
        "detail": room_detail,
        "roomSummary": room_summary,
    })


@app.route('/api/room/transfer', methods=['POST'])
def room_transfer():
    username = user.check_token()
    if not username:
        return flask.jsonify({
            "success": True,
            "reLogin": True,
        })

    target_username = flask.request.json['targetUserName']
    score = flask.request.json['score']
    room_id = flask.request.json['roomId']
    room.room_transfer(room_id, username, target_username, score)
    return flask.jsonify({
        "success": True
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
