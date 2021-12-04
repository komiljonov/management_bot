import requests
from sqlite3 import *
# from constants import *
host = "http://192.168.0.188:8000"


def request_authorization(user_id: str, name_surname: str, description: str, number, user_name: str):
    res = requests.get(f'{host}/create_request/', json={
        "name": str(name_surname),
        "phone": str(number),
        "chat_id": str(user_id),
        "desc": str(description),
        "username": str(user_name)
    })
    if res.status_code == 200:
        return res.json()
    else:
        return None


def check_request_status(user_id: int):
    res = requests.get(f'{host}/check_user/', json={
        "chat_id": user_id
    }).json()
    return res


# check_user(2343434)

# def get_request_types() -> list:
#     res = requests.get(f'{host}/get_request_types/').json()
#     return res['data']



def get_admins_list(user_id: int):
    res = requests.get(f'{host}/admin_list/', json={
        "chat_id": user_id
    })
    return res.json()['data']

def get_users_list(user_id: int):
    res = requests.get(f'{host}/users_list/', json={
        "chat_id": user_id
    })
    return res.json()['data']


def accept_request_admin(user_id: int, req: int) -> bool:
    res = requests.get(f'{host}/update_status/', json={
        "admin": user_id,
        "rq": req,
        "status": 1
    })
    return res.json()


def deny_request_admin(user_id: int, req: int) -> bool:
    res = requests.get(f'{host}/update_status/', json={
        "admin": user_id,
        "rq": req,
        "status": 2
    })
    return res.json()

def get_request_types(user_id:id):
    res = requests.get(f'{host}/request_types/', json={
        "chat_id": user_id,
    })
    return res.json()

def get_req_type(user_id:int, name:str):
    reqs = get_request_types(user_id)
    for req in reqs['data']:
        if req['name'] == name:
            return req
    return None






def get_request(req_id:int):
    res = requests.get(f'{host}/get_request/', json={
        "req": req_id,
    })
    return res.json()

def create_request(user_id:int, req_type:int, req_template:str, req_confirmers:list[int]):
    res = requests.get(f'{host}/create_request/', json={
        "req_type": req_type,
        "request_template": req_template,
        "req_confirmers": req_confirmers,
        "user": user_id
    })
    return res.json()


def get_admins_by_list(admins:list[int], user_id:int):
    res = requests.get(f'{host}/get_admins_by_list/', json={
        "confirmers": admins
    })
    return res.json()



def get_request_from_user(user_id:int, req_id:int):
    res = requests.get(f'{host}/get_request_from_user/', json={
        "req_id": req_id,
    })
    return res.json()