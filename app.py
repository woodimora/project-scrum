from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt
import hashlib

from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

client = MongoClient('54.180.123.225', 27017, username="test", password="test")
db = client.dbscrum

##import pyJWT

SECRET_KEY = 'SCRUM'


# HTML 화면 보여주기
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/api/board', methods=['GET'])
def get_board():
    articles = list(db.boards.find({}, {'_id': False}))
    users = list(db.users.find({}, {'_id': False}))
    return jsonify({'all_article': articles, 'all_user': users})


@app.route('/boards/form')
def view_post_form():
    today = datetime.now().strftime("%Y.%m.%d")
    print(today)
    return render_template('post_form.html', today=today)
# API 역할을 하는 부분
# 게시글 작성
# JWT 사용 함수
# @app.route('/api/board', methods=['POST'])
# def post_board():
# jwt 로드
# token_receive = request.cookies.get('mytoken')
# try:
#     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

# return jsonify({'result': 'success'})
# except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#     return redirect(url_for("home"))

@app.route('/api/boards/add', methods=['POST'])
def post_board():
    print(request.form)
    member_id_receive = request.form['member_id_give']
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']
    emotion_receive = request.form['emotion_give']
    today = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(today)

    print( member_id_receive, title_receive, content_receive, emotion_receive, today)

    doc = {
        'memberId':member_id_receive,
        'title':title_receive,
        'content':content_receive,
        'emotion':emotion_receive,
        'createDate':today,
        'modifiedDate':today,
    }
    db.boards.insert_one(doc);
    return jsonify({'result': 'success', 'msg':'저장이 완료되었습니다.'})

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 3)  # 로그인 3시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
