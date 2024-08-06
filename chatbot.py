from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
import openai
import json
import os
from werkzeug.utils import secure_filename
from models import create_chat_model
from dto import ChatRequestDTO, ChatResponseDTO, ButtonDTO

app = Flask(__name__)
api = Api(app)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
chatbot_namespace = Namespace('chatbot', description='Chatbot operations')
api.add_namespace(chatbot_namespace, path='/chatbot')

# 모델 정의 (Swagger에 나타낼 모델)
chat_model = chatbot_namespace.model('ChatModel', {
    'user_input': fields.String(required=True, description='User input text'),
    'payload': fields.String(description='Payload data'),
    'file': fields.Raw(description='Uploaded file path')
})

# 지역구 버튼 로드 함수
def load_district_buttons():
    with open('districts.json', 'r', encoding='utf-8') as file:
        return json.load(file)["districts"]

district_buttons = load_district_buttons()

# 지역구 정보 로드 함수
def load_districts():
    with open('districts.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# 지역구 홈페이지 URL 로드 함수
def load_district_websites():
    with open('district_websites.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# JSON 파일에서 데이터 로드
districts = load_districts()  # 지역구 정보 로드
district_websites = load_district_websites()  # 지역구 홈페이지 로드

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

# 엔드포인트: 채팅 처리
@chatbot_namespace.route('/')
class Chatbot(Resource):
    @chatbot_namespace.expect(chat_model)
    def post(self):
        # 폼 데이터 및 파일 업로드 처리
        user_input = request.form.get('user_input')  # 사용자 입력 받기
        payload = request.form.get('payload')        # 페이로드 받기
        file = request.files.get('file')             # 파일 받기

        # ChatRequestDTO 생성
        chat_request = ChatRequestDTO(
            user_input=user_input,
            payload=payload,
            photo=None
        )

        # 파일 업로드 처리 로직
        if file:
            filename = secure_filename(file.filename)  # 파일명을 안전하게 변환
            upload_dir = 'uploads' # 업로드 디렉토리 경로 설정
            os.makedirs(upload_dir, exist_ok=True)  # 업로드 디렉토리가 없으면 생성
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)  # 파일을 지정된 경로에 저장
            chat_request.photo = file_path  # DTO에 파일 경로 저장

        # 다양한 페이로드에 따른 응답 처리
        if chat_request.payload == "usage":
            response = ChatResponseDTO(
                message="저는 재활용품과 관련된 여러분들의 궁금증을 해결해드리는 서울리챗입니다!",
                buttons=[
                    ButtonDTO(title="재활용품 지원정책을 알고싶어", payload="policy"),
                    ButtonDTO(title="물건 분리배출 방법을 알고싶어", payload="how_to_dispose")
                ]
            )
        elif chat_request.payload == "policy":
            response = ChatResponseDTO(
                message="재활용품 지원정책에 대해 알려드리겠습니다. 정책 정보를 받아보실 지역구를 선택하거나 직접 메시지를 보내주세요!",
                buttons=[
                    ButtonDTO(title="지역구 선택", payload="select_district"),
                    ButtonDTO(title="직접 입력", payload="input_district")
                ]
            )
        elif chat_request.payload == "select_district":
            response = ChatResponseDTO(
                message="지역구를 선택해주세요.",
                buttons=[
                    ButtonDTO(title=district['title'], payload=district['payload'])
                    for district in district_buttons
                ]
            )
        elif chat_request.payload == "input_district":
            response = ChatResponseDTO(
                message="원하는 지역구를 입력해주세요.",
                buttons=[]
            )
        elif chat_request.payload in district_websites:
            response = ChatResponseDTO(
                message=f"{chat_request.payload}에 대한 정책정보를 확인해주세요.",
                buttons=[
                    ButtonDTO(title=f"{chat_request.payload}청 홈페이지", url=district_websites[chat_request.payload])
                ]
            )
        elif chat_request.payload == "how_to_dispose":
            response = ChatResponseDTO(
                message="분리배출 방법이 궁금한 물건의 사진을 아래 첨부 버튼을 통해 전송해주세요.",
                buttons=[
                    ButtonDTO(title="사진 첨부", payload="upload_photo")
                ]
            )
        elif chat_request.payload == "upload_photo" and chat_request.photo:
            # 사진 인식 시뮬레이션 결과
            recognized_result = "결과 : 플라스틱 병"
            response = ChatResponseDTO(
                message=f"사진을 확인했습니다. 인식된 물건은 {recognized_result}입니다.",
                buttons=[
                    ButtonDTO(title="다른 사진 업로드하기", payload="upload_another")
                ]
            )
        elif chat_request.payload == "upload_another":
            response = ChatResponseDTO(
                message="다른 사진을 업로드해주세요.",
                buttons=[
                    ButtonDTO(title="사진 첨부", payload="upload_photo")
                ]
            )
        else:
            # 기본 처리: OpenAI API를 통한 사용자 입력 처리
            chat_history = ''  # 실제 대화 기록을 여기에 대체
            bot_response = get_response(chat_request.user_input, chat_history)
            response = ChatResponseDTO(
                message=bot_response,
                buttons=[
                    ButtonDTO(title="서울리챗 사용법을 알려줘", payload="usage"),
                    ButtonDTO(title="재활용품 지원정책을 알고 싶어", payload="policy"),
                    ButtonDTO(title="이건 어떻게 버려?", payload="how_to_dispose")
                ]
            )

        # ChatResponseDTO를 JSON으로 변환하여 반환
        return jsonify({
            "message": response.message,
            "buttons": [
                {"title": button.title, "payload": button.payload, "url": button.url}
                for button in response.buttons
            ]
        })
    