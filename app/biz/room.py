from datetime import datetime
from peewee import Model, TextField, DateTimeField, IntegerField
from .db import db


class RoomUser(Model):
    id = IntegerField(
        primary_key=True,
    )
    date = TextField()
    room_id = TextField()
    username = TextField()
    score = IntegerField()
    create_time = DateTimeField()
    update_time = DateTimeField()

    class Meta:
        database = db
        table_name = 'room_user'
        indexes = (
            (('username',), False),
            (('room_id',), False),
            (('date',), False),
            (('room_id', 'username'), True),
        )


class RoomEvent(Model):
    id = IntegerField(
        primary_key=True,
    )
    room_id = TextField()
    from_user = TextField()
    to_user = TextField()
    score = IntegerField()
    create_time = DateTimeField()

    class Meta:
        database = db
        table_name = 'room_event'
        indexes = (
            (('room_id',), False),
        )


db.create_tables([RoomUser, RoomEvent])


def new_room_id() -> (str, str):
    today = datetime.now().strftime("%Y%m%d")
    today_room_set = set()
    room_list = RoomUser.select().where(RoomUser.date == today)
    if room_list:
        for room in room_list:
            today_room_set.add(room.room_id)
    return today, today if not today_room_set else today + '-' + str(len(today_room_set))


def create_room(username: str):
    date, room_id = new_room_id()
    RoomUser.create(
        room_id=room_id,
        username=username,
        date=date,
        score=0,
        create_time=datetime.now(),
        update_time=datetime.now())
    return room_id


def join_room(username: str, room_id: str) -> (bool, str):
    room_user_list = RoomUser.select().where(RoomUser.room_id == room_id)

    if not room_user_list:
        return False, None

    for each in room_user_list:
        if each.username == username:
            # 已经加入过
            return True, room_id

    RoomUser.create(
        room_id=room_id,
        username=username,
        date=room_user_list[0].date,
        score=0,
        create_time=datetime.now(),
        update_time=datetime.now())
    return True, room_id


def convert_score_to_str(score):
    if score <= 0:
        return str(score)
    else:
        return '+' + str(score)


def list_room(username: str):
    room_user_list = RoomUser.select().where(RoomUser.username == username)
    room_info = list()
    if room_user_list:
        for each in room_user_list:
            room = {
                "roomId": each.room_id,
                "status": convert_score_to_str(each.score),
                "createTime": each.create_time,
            }
            room_info.append(room)
    room_info.sort(key=lambda x: x['createTime'], reverse=True)
    for each in room_info:
        del each['createTime']
    return room_info


def room_detail(room_id: str):
    room_user_list = RoomUser.select().where(RoomUser.room_id == room_id)
    detail = list()
    positive_users = list()
    negative_users = list()
    for each in room_user_list:
        detail.append({
            "username": each.username,
            "score": convert_score_to_str(each.score),
        })
        if each.score > 0:
            positive_users.append([each.username, each.score, each.score])
        elif each.score < 0:
            negative_users.append([each.username, each.score, -each.score])

    summary = list()
    if len(positive_users) == 0:
        return detail, summary

    while True:
        positive_users.sort(key=lambda x: x[2], reverse=True)
        negative_users.sort(key=lambda x: x[2])
        negative_user = None
        for each in negative_users:
            if each[2] > 0:
                negative_user = each
                break
        if negative_user is None:
            # 全部分配完成
            break
        idx = 0
        while negative_user[2] > 0:
            assign_cnt = min(negative_user[2], positive_users[idx][2])
            negative_user[2] -= assign_cnt
            positive_users[idx][2] -= assign_cnt
            summary.append({
                "from_user": negative_user[0],
                "to_user": positive_users[idx][0],
                "score": assign_cnt,
            })
            idx += 1
    return detail, summary


def room_transfer(room_id: str, from_username: str, target_username: str, score: int):
    room_user_list = RoomUser.select().where(RoomUser.room_id == room_id)
    for each in room_user_list:
        if each.username == from_username:
            each.score += score
            each.save()
        elif each.username == target_username:
            each.score -= score
            each.save()
    RoomEvent.create(
        room_id=room_id,
        from_user=from_username,
        to_user=target_username,
        score=score,
        create_time=datetime.now())
