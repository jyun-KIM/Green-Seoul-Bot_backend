from flask import Flask
import pymysql



def create_app():
    app = Flask(__name__) # Flask 애플리케이션을 생성


    # DB 연동
    db = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='akidb', charset='utf8')
    
    cursor = db.cursor()

    # query 작성
    sql = "select * from Member"

    cursor.execute(sql)
    

    # db 데이터 가져오기
    print(cursor.fetchall()) # 모든 행 가져오기
    # cursor.fetchone() # 하나의 행만 가져오기
    # cursor.getchmany(n) # n개의 데이터 가져오기

    # 수정 사항 db에 저장
    db.commit

    # 데이터베이스 닫기
    # db.close()
    print('흑흑')

    return app
