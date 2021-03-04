from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb://52.79.73.226', 27017, username="test", password="test")
db = client.dbsparta_plus


@app.route('/cover')
def css():
    return render_template('cover.css')


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]},{'_id':False,'password':False})
        user_info_plus = user_info['username']
        return render_template('index.html', name= user_info_plus)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



@app.route('/contents')
def content():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('contents.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


#
# @app.route('/indexpage')
# def indexpage():
#     return render_template('index.html')


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
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # 키 만들어서 클라이언트에 던져주는 과정

        return jsonify({'result': 'success', 'token': token, 'msg': '로그인 성공!'})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# if __name__ == '__main__':
#     app.run('0.0.0.0', port=5000, debug=True)

######################################
# 조항덕 게시판 글 등록 api 시작
######################################

# from flask import Flask, render_template, jsonify, request
#
# app = Flask(__name__)
#
# from pymongo import MongoClient
#
# client = MongoClient('localhost', 27017)
# db = client.dbsparta


## HTML을 주는 부분
# @app.route('/')
# def home():
#     return render_template('contents.html')


## API 역할을 하는 부분
@app.route('/review', methods=['POST'])
def write_review():
    author_receive = request.form['author_give']
    review_receive = request.form['review_give']
    chapter_receive = request.form['chapter_give']

    doc = {
        'author': author_receive,
        'review': review_receive,
        'chapter': chapter_receive
    }

    db.contenst.insert_one(doc)

    return jsonify({'msg': '등록완료!'})


# @app.route('/review', methods=['GET'])
# def read_reviews():
#     reviews = list(db.contenst.find({}, {'_id': False}))
#     return jsonify({'all_reviews': reviews})

@app.route('/contents/<pn>')
def contents(pn):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]},{'_id':False,'password':False})
        user_info_plus = user_info['username']
        samples = list(db.contenst.find({'chapter': pn}, {'_id': False}))
        sample2 = db.chptbox.find_one({'num': pn})
        middleput = sample2['desc']
        output = sample2['name']
        return render_template('contents.html', name= user_info_plus, samples=samples, middleput=middleput, output=output, pn=pn)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



# token_receive = request.cookies.get('mytoken')
# try:
# payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

# except jwt.ExpiredSignatureError:
#     return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
# except jwt.exceptions.DecodeError:
#     return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# @app.route('/contents/<pnn>')
# def contents2(pnn):
#     sample2 = db.chptbox.find_one({'num': pnn})
#     middleput = sample2['desc']
#     output = sample2['name']
#     # result = list(db.chptbox.find({}, {'_id': False}))
#     return render_template("contents.html", middleput=middleput, output=output)
######################################
# 조항덕 게시판 글 등록 api 끝
#####################################


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
