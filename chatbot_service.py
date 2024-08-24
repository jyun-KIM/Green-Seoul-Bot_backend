from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
import openai
import os
from werkzeug.utils import secure_filename
from config import logger
from generate_chatbot import load_docs, create_vectorstore, create_rag_chain
import json
import torch
#from torch import nn

app = Flask(__name__)
api = Api(app, version='1.0', title='Chatbot API',
        description='A simple chatbot API with policy info and image upload.')

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
chatbot_ns = Namespace('chatbot', description='Chatbot operations')

# Swagger API 문서에서 사용할 모델 정의
chat_model = chatbot_ns.model('Chat', {
    'user_input': fields.String(required=True, description='사용자 인풋')
})

policy_model = chatbot_ns.model('Policy', {
    'district_name': fields.String(required=True, description='지역구')
})

upload_model = chatbot_ns.model('Upload', {
    'district_name': fields.String(required=True, description='지역구'),
    'image_file': fields.String(description='대형 폐기물 사진')
})

# 네임스페이스 등록
api.add_namespace(chatbot_ns, path='/chat')


# 로그 시작
logger.info("로그 시작")


# OpenAI GPT-4 응답 생성 함수
def get_response(user_input):
    try:
        # 문서 로드 및 벡터 스토어 생성
        documents = load_docs() 
        vectorstore = create_vectorstore(documents)

        # RetrievalQA 체인 생성
        qa_chain = create_rag_chain(vectorstore)

        # 질문에 대한 답변 생성
        answer = qa_chain.invoke({"input": user_input})

        # 응답이 복잡한 객체일 경우 문자열로 변환
        if isinstance(answer, dict) and 'text' in answer:
            message = answer['text']
        else:
            message = str(answer)
        
        return message
    
    except Exception as e:
        logger.error(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."


# 사용자 입력 처리
@chatbot_ns.route('/chat')
class Chat(Resource):
    @chatbot_ns.expect(chat_model)
    @chatbot_ns.response(200, 'Success')
    def post(self):
        """사용자 입력처리"""
        try:
            # JSON 형식으로 사용자 입력 받기
            data = request.get_json()
            user_input = data.get("user_input")

            if not user_input:
                return {"error": "user_input이 필요합니다."}, 400

            # OpenAI API를 통해 응답 생성
            message = get_response(user_input)

            # 응답 반환
            return {
                "message": message
            }, 200

        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {"error": "응답을 생성하는 중 오류가 발생했습니다."}, 500


# JSON 파일에서 지역 정보를 로드하는 함수
def load_districts():
    try:
        with open('districts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["districts"]
    except FileNotFoundError:
        logger.error("districts.json 파일을 찾을 수 없습니다.")
        return []


# 정책 정보를 생성하는 함수
def generate_policy_info(district_name):
    try:
        district_name_normalized = district_name.strip()
        districts = load_districts()

        district_url = None
        for district in districts:
            if district["title"].strip() == district_name_normalized:
                district_url = district["district_url"]
                break

        if not district_url:
            return district_name_normalized, "URL 연결오류입니다.", ""

        # OpenAI API를 사용하여 메시지 생성
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing policy information."},
                {"role": "user", "content": f"{district_name_normalized} 정책에 대해 알려줘"}
            ],
            max_tokens=150,
            temperature=0.5,
        )

        message = response['choices'][0]['message']['content'].strip()
        return district_name_normalized, message, district_url

    except Exception as e:
        return district_name, "정책 정보를 불러오는 중 오류가 발생했습니다.", None


# 재활용 지원 정책 정보 조회
@chatbot_ns.route('/policy')
class Policy(Resource):
    @chatbot_ns.expect(policy_model)
    @chatbot_ns.response(200, 'Success')
    def post(self):
        """정책 정보 조회"""
        try:
            data = request.get_json()
            district_name = data.get("district_name")

            if not district_name:
                return {"error": "지역 이름이 필요합니다."}, 400

            district_name, message, district_url = generate_policy_info(district_name)

            return {
                "district_name": district_name,
                "message": message,
                "district_url": district_url
            }, 200

        except Exception as e:
            logger.error(f"Error processing policy request: {e}")
            return {"error": "정책 정보를 생성하는 중 오류가 발생했습니다."}, 500


# 파일 경로에서 district 정보를 불러오는 함수
def get_district_url(district_name):
    try:
        with open('districts.json', 'r', encoding='utf-8') as f:
            district_data = json.load(f)
        for district in district_data['districts']:
            if district['title'] == district_name:
                return district['district_url']
    except FileNotFoundError:
        logger.error("District JSON file not found.")
    return None

def save_image(file):
    file.save('./temp/'+ file.filename)

# 사진 업로드 처리
@chatbot_ns.route('/upload')
class UploadPhoto(Resource):
    @chatbot_ns.expect(upload_model)
    @chatbot_ns.response(200, 'Success')
    def post(self):
        """사진 업로드 처리"""
        try:
            district_name = request.form.get('district_name')
            if not district_name:
                return {"error": "district_name이 제공되지 않았습니다."}, 400

            district_url = get_district_url(district_name)
            if not district_url:
                return {"error": f"'{district_name}'에 해당하는 구를 찾을 수 없습니다."}, 400

            if 'image_file' not in request.files:
                return {"error": "파일이 없습니다."}, 400
            
            file = request.files['image_file']
            if file.filename == '':
                return {"error": "파일 이름이 비어있습니다."}, 400
            
            save_image(file) # 들어오는 이미지 저장
            img = './temp/' + file.filename

            model = torch.hub.load("./yolov5", 'custom', path='./best.pt', source='local')
            
            print("file:", img)
            temp = model(img)
            print(type(temp))
            print("temp:",temp)
            df = temp.pandas().xyxy[0]
            recognized_result = df.name[0]
            return {
                "district_name": district_name,
                "message": f"이 대형폐기물은 {recognized_result}입니다.",
                "district_url": district_url
            }, 200

        except Exception as e:
            logger.error(f"Error processing image upload: {e}", exc_info=True)
            return {"error": "이미지 처리 중 오류가 발생했습니다."}, 500


if __name__ == '__main__':
    app.run(debug=True)