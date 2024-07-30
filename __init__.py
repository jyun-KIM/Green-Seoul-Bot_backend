from flask import Flask
from flask_restx import Api, Namespace, Resource, fields

from .views.main_view import bp
from flask_swagger_ui import get_swaggerui_blueprint
# from flask_jwt_extended import JWTManager


app = Flask(__name__) # Flask 애플리케이션을 생성
# 블루포인트
app.register_blueprint(bp)

@app.route('/')
def hello_pybo():
    return 'Hello World'


# Swagger


api = Api(
    version='0.1',
    title='Akiaka project',
    description='챗봇',
    terms_url='/'
)





# Swagger UI 블루프린트 생성 및 등록
SWAGGER_URL = '/api/docs'  # Swagger UI를 노출할 URL (마지막에 '/' 없음)
API_URL = 'http://localhost:5000/static/swagger.json'  # API url (물론 로컬 리소스일 수 있음)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI 정적 파일이 '{SWAGGER_URL}/dist/'에 매핑됩니다.
    API_URL,
    config={  # Swagger UI 설정
        'app_name': "Test application"
    },
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)



# JWT
# jwt.init_app(app)

if __name__ == '__main__':
    app.run()