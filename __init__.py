from flask import Flask, send_from_directory
from flask_restx import Api
from flask_swagger_ui import get_swaggerui_blueprint
from config import configure_swagger
from chatbot_service import chatbot_ns

def create_app():
    app = Flask(__name__) # Flask 앱 생성

    # API 초기화
    api = Api(app, version='1.0', title='SeoulReChat API', 
              description="OpenAI API를 사용한 AI 챗봇입니다. 사용자가 재활용 지원 정책 정보를 조회하고, 대형 폐기물을 분리수거 할 수 있습니다.",
              doc='/swagger',  # Swagger 문서 위치
              default_label="OpenAI API",
              default="OpenAI API",
              validate=True)

    # Swagger 설정
    configure_swagger(api)

    # 네임스페이스 등록
    api.add_namespace(chatbot_ns, path='/chatbot')
    
    # Swagger UI 설정
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger.json'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "SeoulReChat API",
            'docExpansion': 'full', 
            'layout': "BaseLayout",   # SwaggerHub 스타일에 맞추기 위한 레이아웃 설정
            'filter': True,  # API 필터 사용
        }
    )

    # Swagger UI 블루프린트 등록
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # swagger.json 파일 제공 엔드포인트
    @app.route('/swagger.json')
    def swagger_json():
        return send_from_directory('swagger.json', 'swagger.json')

    return app, api