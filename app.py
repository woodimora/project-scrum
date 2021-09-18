from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
import hashlib
import requests
from werkzeug.utils import secure_filename

from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

client = MongoClient('54.180.150.139', 27017, username="test", password="test")
# client = MongoClient('localhost', 27017)
db = client.dbscrum

##import pyJWT

SECRET_KEY = 'SCRUM'


# HTML 화면 보여주기
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/api/boards', methods=['GET'])
def get_boards():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        now_receive = request.args.get('now_give')

        if now_receive is None:
            now_receive = 0
        else:
            now_receive = int(now_receive)

        total_count = db.boards.count_documents({})
        if total_count > now_receive + 20:
            more_state = True
        else:
            more_state = False

        if now_receive == 0:
            articles = list(db.boards.find({}, {'_id': False}).sort('modifiedDate', -1).limit(20))

        else:
            articles = list(db.boards.find({}, {'_id': False}).sort('modifiedDate', -1).skip(now_receive).limit(20))

        count = len(articles)

        for article in articles:
            member_id = article['memberId']
            user_profile = db.users.find_one({"username":member_id}, {'_id':False,'password':False})
            if user_profile is None:
                article['profile_pic_real'] = "profile_pics/profile_placeholder.png"
            else:
                article['profile_pic_real'] = user_profile["profile_pic_real"]

        return jsonify({'all_article': articles, 'end': now_receive + count ,'count':count, 'state':more_state})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 게시글 양식을 뿌려주는 api
@app.route('/boards/form')
def view_post_form():
    # 쿠키에서 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 시크릿 키를 이용해서 토큰 확인
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 토큰에 있는 아이디가 DB에 있는 유저인지 확인하고 유저정보를 클라이언트에게 전달
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        # 만약 유저정보가 없다면 다시 로그인 페이지로 이동
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        # 오늘 날짜를 화면에 뿌려주기 위해 포멧을 이용하여 변환
        today = datetime.now().strftime("%Y.%m.%d")
        # 오늘 날짜와 유저 정보를 post_form.html 을 랜더링 하면서 함꼐 전달
        return render_template('post_form.html', today=today, user_info=user_info)
    # 토큰을 확인 하였을 때, 로그인 정보가 존재 하지 않거나 만료되면 다시 로그인
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 게시글 작성 api
@app.route('/api/boards/add', methods=['POST'])
def post_board():
    # 쿠키에서 토큰 가져오기
    token_receive = request.cookies.get('mytoken')
    try:
        # 시크릿 키를 이용해서 토큰 확인
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 토큰에 있는 아이디가 DB에 있는 유저인지 확인
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        # 만약 유저정보가 없다면 다시 로그인 페이지로 이동
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

        # 클라이언트로부터 받은 값들을 저장
        member_id = user_info['username']
        title_receive = request.form['title_give']
        content_receive = request.form['content_give']
        emotion_receive = request.form['emotion_give']
        today = datetime.now().isoformat()
        # DB에 저장할 doc 생성
        doc = {
            'memberId': member_id,
            'title': title_receive,
            'content': content_receive,
            'emotion': emotion_receive,
            'createDate': today,
            'modifiedDate': today,
        }
        # DB에 게시글 데이터 저장
        db.boards.insert_one(doc);
        return jsonify({'result': 'success', 'msg': '저장이 완료되었습니다.'})
    # 세션 만료시 에러
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 세션이 만료되었습니다."))
    # 토큰 decode 에러
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 오늘 날짜 게시물 있는지 확인
def check_today(member_id):
    # 오늘 데이터
    today = datetime.now().date().isoformat()
    # 해당 멤버 아이디를 가진 게시물 중에 생성 일자가 오늘인 게시물
    boards = list(db.boards.find({'memberId': member_id, 'createDate': {'$gte': today}}))
    # 오늘 게시물 하나라도 작성을 하였다면 True 출력
    if len(boards) > 0:
        return True
    # 오늘 게시물 하나라도 작성하지 않았다면 False 출력
    else:
        return False


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
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/api/boards/<username>')
def get_user_post(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
        posts = list(db.boards.find({"memberId": username}).sort("modifiedDate", -1))
        for post in posts:
            post["_id"] = str(post["_id"])
        return jsonify({'status': status, 'articles': posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if check_today(username_receive):
        status = 'posted'
    else:
        status = 'not_yet'
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 3)  # 로그인 3시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token, 'post_state': status})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    email_receive = request.form['email_give']
    nickname_receive = request.form['nickname_give']
    profile_info_receive = request.form['profile_info_give']

    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "nickname": nickname_receive,                               # 닉네임
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": profile_info_receive,                       # 프로필 소개글
        "email": email_receive                                      # 이메일
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.users.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/user')
def detail():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        r = requests.get('/api/board')
        response = r.json()
        article = response['all_article']
        return render_template('user.html', article=article)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        email_receive = request.form["email_give"]
        new_doc = {
            "nickname": name_receive,
            "profile_info": about_receive,
            "email": email_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1].lower()
            # print(extension)
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/"+file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/api/boards/delete', methods=['POST'])
def delete_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]}, {'_id':False,'password':False})
        if user_info is None:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
        username_receive = request.form["member_id_give"]
        if username_receive == payload["id"]:  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
            board_id_receive = ObjectId(request.form['board_id_give'])
            db.boards.delete_one({'_id': board_id_receive})
            return jsonify({'msg': '삭제 완료!'})
        else:
            return jsonify({'msg': '삭제 실패!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
