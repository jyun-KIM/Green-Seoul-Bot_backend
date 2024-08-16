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
logger.info("Application started!")


# 사용자 입력 처리
@Chatbot.route('/chat')
class Chat(Resource):
    def post(self):
        """사용자 입력처리"""
        try:
            # JSON 형식으로 사용자 입력 받기
            data = request.get_json()
            user_input = data.get("user_input")

            if not user_input:
                return jsonify({"error": "입력이 필요합니다."}), 400

            # OpenAI API를 통해 응답 생성
            message, district_message = get_response(user_input)

            # 응답 반환
            return jsonify({
                "message": message,
                "district_message": district_message
            })
        
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return jsonify({"error": "응답을 생성하는 중 오류가 발생했습니다."}), 500



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

        # 특정 지역 메시지를 추가 (예시)
        district_message = f"{user_input.split()[0]} 지원정책입니다."

        return message, district_message
    
    except Exception as e:
        logger.error(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요.", ""


# JSON 파일의 district 데이터를 메모리로 로드
with open('districts.json', 'r', encoding='utf-8') as f:
    districts_data = json.load(f)

# district_websites.json 파일을 로드
with open('district_websites.json', 'r', encoding='utf-8') as f:
    district_websites = json.load(f)

def get_policy_info(district_name):
    try:
        documents = load_docs()
        vectorstore = create_vectorstore(documents)
        qa_chain = create_rag_chain(vectorstore)

        question = f"{district_name} 지원정책 알려줘"
        answer = qa_chain.invoke({"input": question})

        # 반환 값이 딕셔너리일 경우 'text' 키 확인
        if isinstance(answer, dict) and 'text' in answer:
            return answer['text']  # 텍스트만 반환

        return str(answer)  # 직렬화 가능하게 문자열로 변환
    except Exception as e:
        logger.error(f"Error fetching policy information: {e}")
        return None
    
# district_name으로 district_url을 찾는 함수
def get_district_url(district_name):
    district_info = next((district for district in district_websites 
                        if district['district_name'] == district_name), None)
    
    return district_info['district_url'] if district_info else None

# 정책 정보 조회
@Chatbot.route('/policy')
class Policy(Resource):
    def post(self):
        """정책 정보 조회"""
        try:
            # 요청으로부터 district_name 받기
            data = request.get_json()
            district_name = data.get("district_name")

            if not district_name:
                return jsonify({"error": "district_name이 필요합니다."}), 400

            # 입력된 district_name을 districts.json에서 검색
            # (정책 정보 txt인지 확인필요)
            district_info = next((district for district in districts_data['districts'] 
                                if district['title'] == district_name), None)
            
            if not district_info:
                return jsonify({"error": f"'{district_name}'에 대한 정보를 찾을 수 없습니다."}), 404

            # OpenAI API를 통해 해당 구의 정책 정보 생성
            policy = get_policy_info(district_name)

            if policy is None:
                return jsonify({"error": f"'{district_name}'에 대한 정책 정보를 가져오는 중 오류가 발생했습니다."}), 500

            # district_websites.json에서 URL 찾기
            district_url = get_district_url(district_name)

            if district_url is None:
                return jsonify({"error": f"'{district_name}'에 대한 URL 정보를 찾을 수 없습니다."}), 404

            # 응답 반환
            return jsonify({
                "district_name": district_name,
                "message": policy,
                "district_url": district_url
            })

        except Exception as e:
            logger.error(f"정책 정보를 처리하는 중 오류 발생: {e}", exc_info=True)
            return jsonify({"error": "정책 정보를 조회하는 중 오류가 발생했습니다.", "details": str(e)}), 500
        





# 파일이 저장될 디렉토리
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 파일 확장자 확인 함수
def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 사진 업로드 처리
@Chatbot.route('/upload')
class UploadPhoto(Resource):
    def post(self):
        """사진 업로드 처리"""
        try:
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

            # 응답 반환 (문자열로 인식된 물건을 반환)
            recognized_result = "플라스틱 병"  # 여기서 실제로 yolo 모델이 분석한 결과를 반환해야 함
            return {"message": f"인식된 물건은 {recognized_result}입니다."}, 200

        except Exception as e:
            # 오류 발생 시 로그 기록 후 에러 메시지 반환
            logger.error(f"Error processing image upload: {e}", exc_info=True)
            return {"error": "이미지 처리 중 오류가 발생했습니다."}, 500
        
if __name__ == '__main__':
    app.run(debug=True)