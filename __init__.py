from flask import Flask
from flask_restx import Api
from config import configure_swagger
from chatbot import chatbot_namespace

def create_app():
    # Flask 앱 생성
    app = Flask(__name__)

    # API 초기화
    api = Api(app, version='1.0', title='SeoulReChat API', description='SeoulReChat AI Chatbot API')

    # Swagger 설정
    configure_swagger(api)

    # 네임스페이스 등록
    api.add_namespace(chatbot_namespace, path='/chatbot')
    

    return app