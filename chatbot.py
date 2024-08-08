from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
import openai
import os
from werkzeug.utils import secure_filename
from models import define_models
from config import logger
from dto import ImageUploadDTO, PolicyInfoDTO, UserInputDTO, ImageUploadResponseDTO, PolicyInfoResponseDTO, ChatResponseDTO
import json

# DTO랑 Model 없애기

app = Flask(__name__)
api = Api(app)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
Chatbot = Namespace('Chatbot')

# 모델 정의 (Swagger에 나타낼 모델)
image_upload_model, policy_info_model, user_input_model, photo_upload_response_model, policy_info_response_model, chat_response_model = define_models(Chatbot)

# 로그 시작
logger.info("Application started!")

# OpenAI GPT-3.5 Turbo 응답 생성 함수
def get_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=2000,
            messages=[{"role": "user", "content": user_input}]
        )
        chatgpt_output = response.choices[0].message['content']
        logger.info(f"OpenAI GPT-3.5 Turbo 응답: {chatgpt_output}")  # 응답을 로그로 출력
        return chatgpt_output
    except Exception as e:
        print(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."

# 지역구 홈페이지 URL 로드 함수
def load_district_websites():
    with open('district_websites.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 파일에서 데이터 로드
district_websites = load_district_websites()  # 지역구 홈페이지 로드

# 사진 업로드 처리
@Chatbot.route('/upload')
class UploadPhoto(Resource):
    @Chatbot.expect(image_upload_model)
    @Chatbot.response(200, 'Success', ImageUploadResponseDTO)
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
        return jsonify({"message":f"인식된 물건은 {recognized_result}입니다."})

# 정책 정보 조회
@Chatbot.route('/policy')
class Policy(Resource):
    @Chatbot.expect(policy_info_model)
    @Chatbot.response(200, 'Success', PolicyInfoResponseDTO)
    def post(self):
        print('흑흑흑')
        """정책 정보 조회"""
        data = request.json
        district_name = data.get('district_name')

        if district_name not in district_websites:
            return jsonify({"message": "해당 지역구의 정보를 찾을 수 없습니다."}), 400

        # ChatGPT를 통해 응답 생성
        user_input = f"{district_name} 정책정보 알려줘"
        bot_response = get_response(user_input)
        
        # 정책 정보와 홈페이지 링크를 결합하여 반환
        homepage_url = district_websites[district_name]
        message = f"{bot_response}\n{district_name} 홈페이지: {homepage_url}"
        return jsonify({"message": message, "homepage_url": homepage_url})

    
# 사용자 입력 처리
@Chatbot.route('/chat')
class Chat(Resource):
    @Chatbot.expect(user_input_model)
    @Chatbot.response(200, 'Success', chat_response_model)
    def post(self):
        """사용자 입력처리"""
        data = request.json
        user_input = data.get(user_input)

        if not user_input:
            return jsonify({"message": "입력해주세요."}), 400
    
        bot_response = get_response(user_input)

        logger.info(f"사용자 입력: {user_input}, 챗봇 응답: {bot_response}")

        return jsonify({"message": bot_response})


if __name__ == '__main__':
    app.run(debug=True)