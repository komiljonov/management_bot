import requests
from constants import *
host = "http://192.168.0.188:8000"


def request_authorization(user_id: str, name_surname: str, description: str, number, user_name: str) -> dict | None:
    a = [user_id, name_surname, description, number, user_name]
    for i in a:
        print(type(i))
    res = requests.get(f'{host}/create_request/', json={
        "name": str(name_surname),
        "phone": str(number),
        "chat_id": str(user_id),
        "desc": str(description),
        "username": str(user_name)
    })

    print(res.json())

    if res.status_code == 200:
        return res.json()
    else:
        return None


def check_request_status(user_id: int) -> int | None:
    res = requests.get(f'{host}/check_user/', json={
        "chat_id": user_id
    }).json()
    print(res)
    return res['status']


# check_user(2343434)

def get_request_types() -> list:
    """ {
       "ok": True,
       "data": [{
                "id": 1,
                "name": "Chiqim"
                }
            ]
      }"""
    res = requests.get(f'{host}/get_request_types/').json()
    return res['data']


def get_admins_list() -> list | None:
    """ {
       "ok": True,
       "data": [{
                "chat_id": 1231233
                }
            ]
      }"""
    res = requests.get(f'{host}/get_request_types/').json()
    return res['data']