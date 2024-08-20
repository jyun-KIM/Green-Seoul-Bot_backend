from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource
import openai
import os
from werkzeug.utils import secure_filename
from config import logger
from generate_chatbot import load_rewardPolicy, create_vectorstore, processing_user_input,  processing_image

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64
import httpx


app = Flask(__name__)
api = Api(app)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
Chatbot = Namespace('Chatbot')

# 로그 시작
logger.info("Application started!")

# OpenAI GPT-4o 응답 생성 함수    
def get_response1(user_input):
    try:
        # 문서 로드 및 벡터 스토어 생성
        documents = load_rewardPolicy() 
        vectorstore = create_vectorstore(documents)

        # RetrievalQA 체인 생성
        qa_chain = processing_user_input(vectorstore)
        answer = qa_chain.invoke({"input": user_input})


        return answer
    
    except Exception as e:
        print(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."
    

    # OpenAI GPT-4o 응답 생성 함수    
def get_response_img():
    try:
        answer = processing_image()

        print("cc")
        #print(answer)

        #print(answer.content)

        return answer
    
    except Exception as e:
        print(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."


# 테스트용 엔드포인트
@Chatbot.route('/test')
class TestAPI(Resource):
    def post(self):
        """OpenAI API 테스트"""
        if not request.is_json:
            return jsonify({"message": "JSON 형식으로 요청해주세요."}), 400

        data = request.get_json()
        user_input = data.get('user_input')

        if not user_input:
            return jsonify({"message": "입력해주세요."}), 400

        bot_response = get_response_img(user_input)

        # API 응답 반환
        return jsonify({"message": bot_response}), 200




# 지역구 홈페이지 URL 로드 함수
def load_district_websites():
    with open('district_websites.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 파일에서 데이터 로드
district_websites = load_district_websites()  # 지역구 홈페이지 로드

# 파일이 저장될 디렉토리
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 파일 확장자 확인 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 사진 업로드 처리
@Chatbot.route('/upload')
class Chat(Resource):
    def post(self):
        """사용자 입력처리
        data = request.get_json()
        print(data)
        user_input = data['user_input']
        
        if not user_input:
            return jsonify({"message": "입력해주세요."}), 400
    
        """

        bot_response = get_response_img()
        print("bot_response",bot_response, "finish bot_response")
        #answer = bot_response['answer']

        return jsonify({"message": bot_response})

            

# 정책 정보 조회
@Chatbot.route('/policy')
class Policy(Resource):
    def post(self):
        """정책 정보 조회"""
        if not request.is_json:
            return jsonify({"message": "JSON 형식으로 요청해주세요."}), 400
        
        districtData = request.get_json('district_name')
        district_name = districtData['district_name']
        print(district_name)

        if not district_name:
            return jsonify({"message": "지역구 이름을 입력해주세요."}), 400

        '''
        if district_name not in district_websites:
            print("fd")
            return jsonify({"message": "해당 지역구의 정보를 찾을 수 없습니다."}), 400
        '''

    # ChatGPT를 통해 응답 생성
        bot_response = get_response1(district_name)
        message = bot_response['answer']
      
        
        # 정책 정보와 홈페이지 링크를 결합하여 반환
        homepage_url = next(item["district_url"] for item in district_websites if item["district_name"] == district_name)
        
        return jsonify({"message": message, "homepage_url": homepage_url})
    
# 사용자 입력 처리
@Chatbot.route('/chat')
class Chat(Resource):
    def post(self):
        """사용자 입력처리"""
        data = request.get_json('user_input')
        #print(data)
        user_input = data['user_input']
        

        if not user_input:
            return jsonify({"message": "입력해주세요."}), 400
    
        bot_response = get_response1(user_input)
        print(bot_response)
        answer = bot_response['answer']

        return jsonify({"message": answer})



if __name__ == '__main__':
    app.run(debug=True)

