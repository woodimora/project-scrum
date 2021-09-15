from pymongo import MongoClient
from datetime import datetime

from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

client = MongoClient('54.180.123.225', 27017, username="test", password="test")
db = client.dbscrum

# import pyJWT
import jwt

SECRET_KEY = 'SCRUM'


# HTML 화면 보여주기
@app.route('/')
def home():
    today = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(today)
    return render_template('index.html')

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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
