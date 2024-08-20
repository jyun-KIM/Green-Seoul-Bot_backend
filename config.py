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
    api = Api(app, title='SeoulRechat API', version='1.0', description='OpenAI API를 사용한 AI 챗봇입니다. 사용자가 재활용 지원 정책 정보를 조회하고, 대형 폐기물을 분리수거 할 수 있습니다.')


    return app, api