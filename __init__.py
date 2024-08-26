from flask import Flask
from flask_restx import Api
from config import configure_swagger
from chatbot_service import Chatbot

def create_app():
    # Flask 앱 생성
    app = Flask(__name__)
    # API 초기화
    api = Api(app, version='1.0', title='SeoulReChat API', description='SeoulReChat AI Chatbot API')
    api = Api(app, version='1.0', title='SeoulReChat API', 
            description="OpenAI API를 사용한 AI 챗봇입니다. 사용자가 재활용 지원 정책 정보를 조회하고, 대형 폐기물을 분리수거 할 수 있습니다.",
            doc='/swagger',  # Swagger 문서 위치
            default_label="OpenAI API",
            default="OpenAI API",
            validate=True)

    # Swagger 설정
    configure_swagger(api)
    # 네임스페이스 등록
    api.add_namespace(Chatbot, path='/chatbot')
    

    return app, api