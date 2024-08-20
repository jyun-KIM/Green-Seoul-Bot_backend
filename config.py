from flask import Flask
from flask_cors import CORS
from flask_restx import Api
import os
import logging


# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def create_app():
    app = Flask(__name__) # Flask 애플리케이션 생성

    # CORS 설정 추가
    CORS(app)

    # API 객체 생성 및 앱에 등록
    api = Api(app)


    return app, api