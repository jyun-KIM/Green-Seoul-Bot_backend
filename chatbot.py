from flask import Flask, request, jsonify, make_response
from flask_restx import Api, Namespace, Resource
import openai
import os
from werkzeug.utils import secure_filename
from config import logger
from generate_chatbot import load_rewardPolicy, create_vectorstore, create_rag_chain
import json
from langchain_openai import ChatOpenAI
import httpx


app = Flask(__name__)
api = Api(app, version='1.0', title='Chatbot API',
        description='A simple chatbot API with policy info and image upload.')

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
Chatbot = Namespace('Chatbot')

# 네임스페이스 등록
api.add_namespace(Chatbot, path='/chat')

# 로그 시작
logger.info("Application started!")

# OpenAI GPT-4o 응답 생성 함수    
def get_response(user_input):
    try:
        # 문서 로드 및 벡터 스토어 생성
        documents = load_rewardPolicy() 
        vectorstore = create_vectorstore(documents)

        # RetrievalQA 체인 생성
        qa_chain = create_rag_chain(vectorstore)
        answer = qa_chain.invoke({"input": user_input})


        return answer
    
    except Exception as e:
        print(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."



# 지역구 홈페이지 URL 로드 함수
def load_district_websites():
    with open('district_websites.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 파일에서 데이터 로드
district_websites = load_district_websites()  # 지역구 홈페이지 로드
            

# 정책 정보 조회
@Chatbot.route('/policy')
class Policy(Resource):
    def post(self):
        """정책 정보 조회"""
        if not request.is_json:
            return make_response(jsonify({"message": "JSON 형식으로 요청해주세요."}), 400)
        
        districtData = request.get_json('district_name')
        district_name = districtData['district_name']

        if not district_name:
            return make_response(jsonify({"message": "지역구 이름을 입력해주세요."}), 400)

        #주어진 지역구 이름이 district_websites에 존재하는지 확인
        if not any(item["district_name"] == district_name for item in district_websites):
            return make_response (jsonify({"message": "해당 지역구의 정보를 없습니다."}), 400)
    

    # ChatGPT를 통해 응답 생성
        bot_response = get_response(district_name)
        message = bot_response['answer']
      
        
        # 정책 정보와 홈페이지 링크를 결합하여 반환
        homepage_url = next(item["district_url"] for item in district_websites if item["district_name"] == district_name)
        
        return jsonify({"message": message, "district_url": homepage_url})
    
# 사용자 입력 처리
@Chatbot.route('/chat')
class Chat(Resource):
    def post(self):
        """사용자 입력처리"""
        data = request.get_json('user_input')
        user_input = data['user_input']
        
        if not user_input:
            return make_response(jsonify({"message": "입력해주세요."}), 400)
    
        bot_response = get_response(user_input)
        answer = bot_response['answer']

        return jsonify({"message": answer})



if __name__ == '__main__':
    app.run(debug=True)

