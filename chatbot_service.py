from flask import Flask, request, jsonify, make_response
from flask_restx import Api, Namespace, Resource, fields
import openai
import os
from werkzeug.utils import secure_filename
from config import logger
from generate_chatbot import load_rewardPolicy, create_vectorstore, create_rag_chain
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
        documents = load_rewardPolicy() 
        vectorstore = create_vectorstore(documents)

        # RetrievalQA 체인 생성
        qa_chain = create_rag_chain(vectorstore)
        answer = qa_chain.invoke({"input": user_input})


        return answer
    
    except Exception as e:
        print(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."


# 사용자 입력 처리
@chatbot_ns.route('/chat')
class Chat(Resource):
    @chatbot_ns.expect(chat_model)
    @chatbot_ns.response(200, 'Success')
    def post(self):
        try:
            """사용자 입력처리"""
            data = request.get_json('user_input')
            user_input = data['user_input']
            
            if not user_input:
                return make_response(jsonify({"message": "입력해주세요."}), 400)

            bot_response = get_response(user_input)
            answer = bot_response['answer']

            return make_response(jsonify({"message": answer}), 200)

        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {"error": "응답을 생성하는 중 오류가 발생했습니다."}, 500



# 지역구 홈페이지 URL 로드 함수
def load_district_websites():
    with open('district_websites.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 파일에서 데이터 로드
district_websites = load_district_websites()  # 지역구 홈페이지 로드


# 재활용 지원 정책 정보 조회
@chatbot_ns.route('/policy')
class Policy(Resource):
    @chatbot_ns.expect(policy_model)
    @chatbot_ns.response(200, 'Success')
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
            img = './upliads/' + file.filename

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