from flask import Flask
from config import create_app
from chatbot_service import chatbot_ns
from flask_cors import CORS


app, api = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})   # 모든 도메인에서의 요청을 허용

api.add_namespace(chatbot_ns,'/chatbot')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)
