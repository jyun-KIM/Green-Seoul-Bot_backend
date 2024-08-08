from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
import openai
import json
import os
from werkzeug.utils import secure_filename
from models import define_models

app = Flask(__name__)
api = Api(app)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
chatbot_namespace = Namespace('chatbot', description='Chatbot operations')

# 모델 정의 (Swagger에 나타낼 모델)
image_upload_model, policy_info_model, user_input_model = define_models(chatbot_namespace)

# OpenAI GPT-3.5 Turbo 응답 생성 함수
def get_response(user_input, chat_history):
    try:
        messages = [
            {"role": "system", "content": f"Conversation history: {chat_history}"},
            {"role": "user", "content": user_input}
        ]
    
        # OpenAI API를 사용하여 GPT-3.5 Turbo 모델로부터 응답 생성
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=2000,
            messages=messages
        )
        
        chatgpt_output = response.choices[0].message['content']
        return chatgpt_output
    except Exception as e:
        print(f"end=Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."

# 지역구 홈페이지 URL 로드 함수
def load_district_websites():
    with open('district_websites.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 파일에서 데이터 로드
district_websites = load_district_websites()  # 지역구 홈페이지 로드

# 사진 업로드 처리
@chatbot_namespace.route('/upload')
class UploadPhoto(Resource):
    @chatbot_namespace.expect(image_upload_model)
    def post(self):
        """사진 업로드 처리"""
        file = request.files.get('file')

        if not file:
            return jsonify({"message":"파일이 첨부되지 않았습니다."}), 400
        
        filename = secure_filename(file.filename)
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # 테스트
        recognized_result = "플라스틱 병" 
        return jsonify({"message":r"인식된 물건은 {recognized_result}입니다."})
    
# 정책 정보 조회
@chatbot_namespace.route('/policy')
class Policy(Resource):
    @chatbot_namespace.expect(policy_info_model)
    def post(self):
        """정책 정보 조회"""
        data = request.json
        district_name = data.get('district_name')

        # 테스트
        message = f"{district_name}청 재활용품 지원 정책입니다."
        return jsonify({"message": message})
    
# 사용자 입력 처리
@chatbot_namespace
class Chat(Resource):
    @chatbot_namespace.expect(user_input_model)
    def post(self):
        """사용자 입력처리"""
        data = request.json
        user_input =data.get(user_input)

        if not user_input:
            return jsonify({"message": "입력해주세요."}), 400
        
        bot_response = get_response(user_input)
        return jsonify({"message": bot_response})