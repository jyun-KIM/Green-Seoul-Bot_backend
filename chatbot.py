from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource
import openai
import os
from werkzeug.utils import secure_filename
from config import logger
from generate_chatbot import load_docs, create_vectorstore, create_rag_chain
import json


app = Flask(__name__)
api = Api(app)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 네임스페이스 정의
Chatbot = Namespace('Chatbot')

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
            message = str(answer)  # 직렬화 가능하도록 문자열 변환

        # 특정 지역 메시지를 추가
        district_message = f"{user_input.split()[0]} 지원정책입니다."
        
        return message, district_message
    
    except Exception as e:
        logger.error(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요.", ""


# 사용자 입력 처리
@Chatbot.route('/chat', methods=['POST'])
class Chat(Resource):
    def post(self):
        """사용자 입력처리"""
        try:
            # JSON 형식으로 사용자 입력 받기
            data = request.get_json()
            user_input = data.get("user_input")

            if not user_input:
                return jsonify({"error": "district_name 입력이 필요합니다."}), 400

            # OpenAI API를 통해 응답 생성
            message, district_message = get_response(user_input)

            # message, district_message 로직 추가해야함


            # 응답 반환
            return jsonify({
                "message": message,
                "district_message": district_message
            })
        
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return jsonify({"error": "응답을 생성하는 중 오류가 발생했습니다."}), 500


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
        # 입력된 지역명을 그대로 사용하여 비교
        district_name_normalized = district_name.strip()

        # JSON 파일에서 지역 정보를 로드
        districts = load_districts()

        # 지역에 맞는 URL 찾기
        district_url = None
        for district in districts:
            logger.info(f"Checking district: {district['title']}")
            if district["title"].strip() == district_name_normalized:
                district_url = district["district_url"]
                logger.info(f"Found URL for {district_name_normalized}: {district_url}")
                break

        # 지역 URL을 찾지 못하면 오류 메시지 반환
        if not district_url:
            return district_name_normalized, "URL 연결오류", ""

        # OpenAI API 호출을 주석 처리하고 URL만 반환
        # OpenAI API를 사용하여 메시지 생성
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo", 
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant providing policy information."},
        #         {"role": "user", "content": f"{district_name_normalized} 정책에 대해 알려줘"}
        #     ],
        #     max_tokens=150,
        #     temperature=0.5,
        # )

        # 응답 메시지 추출
        # message = response['choices'][0]['message']['content'].strip()

        # 디버깅을 위해 임시 메시지 반환
        message = f"{district_name_normalized} 정책에 대한 임시 메시지."

        return district_name_normalized, message, district_url

    except Exception as e:
        logger.error(f"Error fetching response from OpenAI: {e}")
        return district_name, "정책 정보를 불러오는 중 오류가 발생했습니다.", district_url



# 정책 엔드포인트
@Chatbot.route('/policy', methods=['POST'])
class Policy(Resource):
    def post(self):
        """정책 정보 조회"""
        try:
            # JSON 형식으로 사용자 입력 받기
            data = request.get_json()
            district_name = data.get("district_name")

            if not district_name:
                return jsonify({"error": "지역 이름이 필요합니다."}), 400

            # 정책 정보 생성
            district_name, message, district_url = generate_policy_info(district_name)

            # 응답 반환
            return jsonify({
                "district_name": district_name,
                "message": message,
                "district_url": district_url
            })

        except Exception as e:
            logger.error(f"Error processing policy request: {e}")
            return jsonify({"error": "정책 정보를 생성하는 중 오류가 발생했습니다."}), 500


# 파일이 저장될 디렉토리
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 허용된 파일 확장자인지 확인
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 파일 경로에서 district 정보를 불러오는 함수
def get_district_url(district_name):
    """district_name에 맞는 district_url을 반환"""
    try:
        with open('district_websites.json', 'r', encoding='utf-8') as f:
            district_data = json.load(f)
        for district in district_data:
            if district['district_name'] == district_name:
                return district['district_url']
    except FileNotFoundError:
        logger.error("District websites JSON file not found.")
    return None

# 사진 업로드 처리
@Chatbot.route('/upload', methods=['POST'])
class UploadPhoto(Resource):
    def post(self):
        """사진 업로드 처리"""
        try:
            # 요청 JSON에서 데이터 추출
            district_name = request.form.get('district_name')
            if not district_name:
                logger.error("district_name이 제공되지 않았습니다.")
                return {"error": "district_name이 제공되지 않았습니다."}, 400
            
            # district_name에 맞는 URL 검색
            district_url = get_district_url(district_name)
            if not district_url:
                logger.error(f"'{district_name}'에 해당하는 구를 찾을 수 없습니다.")
                return {"error": f"'{district_name}'에 해당하는 구를 찾을 수 없습니다."}, 400

            # 파일이 제대로 업로드 되었는지 확인
            if 'image_file' not in request.files:
                logger.error("파일이 없습니다.")
                return {"error": "파일이 없습니다."}, 400
            
            file = request.files['image_file']
            
            if file.filename == '':
                logger.error("파일 이름이 비어있습니다.")
                return {"error": "파일 이름이 비어있습니다."}, 400

            # 파일 확장자 확인
            if not allowed_file(file.filename):
                logger.error("허용되지 않는 파일 형식입니다.")
                return {"error": "허용되지 않는 파일 형식입니다."}, 400

            # 파일 저장
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            file.save(file_path)
            logger.info(f"파일이 성공적으로 저장되었습니다: {file_path}")

            # 응답 반환
            recognized_result = "플라스틱 병"  # 여기서 yolo 모델이 분석한 결과를 반환해야 함
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