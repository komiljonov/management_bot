from . import db
from .keyboards import *
from .msg_id import msg_db



import random

def send_code_to_sms(number):
    code = random.randint(111111, 999999)
    #code to send verification code by api
    print(code)
    return code


def is_odd(a):
    return bool(a - ((a >> 1) << 1))






def distribute(items, number) -> list:
    res = []
    start = 0
    end = number
    for item in items:
        if items[start:end] == []:
            return res
        res.append(items[start:end])
        start += number
        end += number
    return res


def format_number(string:str):
        string  = str(string)
        j = len(string) % 3
        substrings = [string[3 * i + j:3 * (i + 1) + j] for i in range(len(string)//3)]
        if j != 0:
            substrings.insert(0, string[:j])
        return " ".join(substrings)


def is_confirmer(req, user):
    
    for conf in req['req_type']['confirmers']:
        if conf['chat_id'] == user.id:
            return True
    return False

DASHES = '-' * 30
statuses = ["kutilmoqda", "tasdiqlandi", "rad etildi"]
def format_request_to_text(req:dict):
    print(req)
    confers_text = ""
    print(req)
    for coner in req['req_type'].get('confirmers', []):
        confers_text += f"{coner['name']} @{coner['username']}"
    text = f"""<b>So'rov raqami:</b> {req['id']}
<b>So'rov turi:</b> {req['req_type']['name']}\n<b>So'rov malumotlari:</b>
<b>{DASHES}</b>
{req['template']}
{DASHES}
<b>Tasdiqlovchilar:</b>
{DASHES}
{ confers_text }
{DASHES}
<b>Xolati:</b>{statuses[req['status']]}
{ f"<b>{ 'Tasdiqladi' if req['status'] == 1 else 'Rad etdi' }:</b> {req['confirmer']['name']} (@{req['confirmer']['username']})" if req['status'] != 0 else "" }
<b>Yuboruvchi:</b> {req['user']['name']} (@{req['user']['username']})"""
    return text



import requests

def download_file(url):
    local_filename = f"data.xlsx" 
    # NOTE the stream=True parameter below
    print(local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return open(local_filename, 'rb')