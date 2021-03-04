from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb://localhost', 27017)
db = client.dbsparta_plus


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]},{'_id':False,'password':False})  ## 진자용
        user_info_plus = user_info['username']
        return render_template('index.html', name= user_info_plus)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


# db 작업 초기 1회용
# doc = [{'num': '1', 'name': 'chapter 1 : 웹개발 미니 프로젝트', 'desc': '사전준비 지식을 바탕으로, 첫 번째 팀 프로젝트 완성해보기'},
#         {'num': '2', 'name': 'chapter 2 : 자료구조, 알고리즘', 'desc': '매일 할당된 알고리즘을 풀어내기, 문제은행의 바다에 빠져보기'},
#         {'num': '3', 'name': 'chapter 3 : 주특기 기본/심화', 'desc': '주특기 기본/심화에 맞춰 필요한 기술을 적용하며 프로젝트 2회 완성'},
#         {'num': '4', 'name': 'chapter 4 : 클론코딩', 'desc': '실제 서비스를 클론코딩하며 실전 퀄리티에 대비하기'},
#         {'num': '5', 'name': 'chapter 5 : 미니프로젝트', 'desc': '각자의 주특기를 가지고 2주만에 실제 서비스를 만들어 런칭'},
#         {'num': '6', 'name': 'chapter 6 : 실전프로젝트', 'desc': '디자이너와 협업하며 4주만에 실제 프로젝트를 런칭하고, 1주 동안 고객의 의견을 모아 개선'},
#         {'num': '7', 'name': 'chapter 7 : 지원하기', 'desc': '이력서를 작성하고, 면접을 연습하고 -> 협력사에 지원하기'}]
# db.chptbox.insert_many(doc)