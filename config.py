from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
import os
import pymysql
from flask_restx import Api, Resource, fields, Namespace # Api 구현을 위한 객체 import

app = Flask(__name__)
swagger = Swagger(app)

# swagger 설정
def configure_swagger(api):
    api.title = 'Chatbot API'
    api.version = '1.0'

# gitignore 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# DB 설정
def create_app():
    app = Flask(__name__) # Flask 애플리케이션을 생성

    # CORS 설정 추가
    CORS(app)

    # Swagger 설정
    swagger = Swagger(app)
    configure_swagger(swagger)

    # DB 연동
    try:
        db = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='akidb', charset='utf8')
        
        cursor = db.cursor()

        # query 작성
        sql = "select * from member"
        cursor.execute(sql)
        

        # db 데이터 가져오기
        print(cursor.fetchall()) # 모든 행 가져오기
        # cursor.fetchone() # 하나의 행만 가져오기
        # cursor.getchmany(n) # n개의 데이터 가져오기

        # 수정 사항 db에 저장
        db.commit

        # 데이터베이스 닫기
        # db.close()

    except Exception as e:
        print(f"An error occurred: {e}")

    return app


# AWS


app = create_app()