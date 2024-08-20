from flask import Flask, send_from_directory
from flask_restx import Api
from flask_swagger_ui import get_swaggerui_blueprint
from config import configure_swagger
from chatbot import Chatbot

def create_app():
    # Flask 앱 생성
    app = Flask(__name__)
    # API 초기화
    api = Api(app, version='1.0', title='SeoulReChat API', description='SeoulReChat AI Chatbot API')

    # Swagger 설정
    configure_swagger(api)

    # 네임스페이스 등록
    api.add_namespace(Chatbot, path='/chatbot')

    # Swagger UI 설정
    SWAGGER_URL = '/swagger' # Swagger UI가 제공될 경로
    API_URL = '/swagger.json' # swagger.json 파일 경로

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "SeoulRechat API",
            'cacheControl': "no-cache"
        }
    )

    # Swagger UI 블루프린트 등록
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # swagger.json 파일 제공 엔드포인트
    @app.route('/swagger.json')
    def swagger_json():
        return send_from_directory('.', 'swagger.json')

    return app, api