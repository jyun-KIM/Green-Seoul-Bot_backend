from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource
import openai
import os
from werkzeug.utils import secure_filename
from config import logger
import json


app = Flask(__name__)
api = Api(app)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
Chatbot = Namespace('Chatbot')

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
        chatgpt_output = response['choices'][0]['message']['content']
        logger.info(f"OpenAI GPT-3.5 Turbo 응답: {chatgpt_output}")  # 응답을 로그로 출력
        return chatgpt_output
    except Exception as e:
        logger.error(f"Error fetching response from OpenAI: {e}")
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

        bot_response = get_response(user_input)

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
class UploadPhoto(Resource):
    def post(self):
        """사진 업로드 처리"""
        try:
            # 파일이 요청에 포함되어 있는지 확인
            if 'image_file' not in request.files:
                return jsonify({"message": "파일이 첨부되지 않았습니다."}), 400
            
            file = request.files['image_file']

            # 파일 이름이 있는지 확인
            if file.filename == '':
                return jsonify({"message": "파일 이름이 비어 있습니다."}), 400

            # 파일이 허용된 형식인지 확인
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # 디렉토리가 없으면 생성
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # 파일 저장
                file.save(file_path)

                # 파일 업로드 성공 메시지 반환 (예: 인식된 물체 이름을 반환)
                recognized_result = "can"  # 여기에 실제 인식 결과를 넣을 수 있습니다.
                return jsonify({"message": f"The object recognized is a {recognized_result}"}), 200
            else:
                return jsonify({"message": "허용되지 않는 파일 형식입니다."}), 400
        
        except Exception as e:
            logger.error(f"Error during file upload: {e}", exc_info=True)  # 에러 로그 추가
            return jsonify({"message": "서버 오류가 발생했습니다.", "error": str(e)}), 500

# 정책 정보 조회
@Chatbot.route('/policy')
class Policy(Resource):
    def post(self):
        """정책 정보 조회"""
        if not request.is_json:
            return jsonify({"message": "JSON 형식으로 요청해주세요."}), 400
        
        data = request.get_json()
        district_name = data.get('district_name')

        if not district_name:
            return jsonify({"message": "지역구 이름을 입력해주세요."}), 400

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
    def post(self):
        """사용자 입력 처리"""
        if not request.is_json:
            return jsonify({"message": "JSON 형식으로 요청해주세요."}), 400
        
        data = request.get_json()
        user_input = data.get('user_input')

        if not user_input:
            return jsonify({"message": "입력해주세요."}), 400
    
        bot_response = get_response(user_input)

        logger.info(f"사용자 입력: {user_input}, 챗봇 응답: {bot_response}")

        return jsonify({"message": bot_response})


if __name__ == '__main__':
    app.run(debug=True)