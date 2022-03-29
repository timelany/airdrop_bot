import re, time, random
from datetime import datetime
from types import NoneType
from .client import Client
from telethon import events, sync


def get_client(sessions, api:tuple):
    try:
        api_id, api_hash = api

        client = Client().set_session(sessions).set_apiId(api_id).set_apiHash(api_hash).perform().get()
        return client
    except Exception as e:
        return False
        

async def set_time_out(last_message_received_on: datetime):
    timeout = datetime.now() - last_message_received_on
    while True:
        # Nếu hiện tại không được set tin nhắn hoặc thời gian đếm ngược lớn hơn 2s thì disconnect
        if not last_message_received_on and timeout.seconds > 2:
            # Các hành động nếu timeout
            print(' [+] Disconnected! ')
            return False
        else: 
            return True

def cleant_text(text):

    recompile = re.compile("[\n\t\r.,]")

    message_clean = recompile.sub("", text)

    return message_clean
    
def sleep(time_sleep: int = None):
    if not time_sleep:
        rand = random.randint(1,3)
        time.sleep(rand)
    else: time.sleep(time_sleep)

def captcha_solve():
    ...
