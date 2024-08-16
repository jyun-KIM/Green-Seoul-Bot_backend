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

# OpenAI GPT-4o 응답 생성 함수
def get_response(user_input):
    try:
        # 문서 로드 및 벡터 스토어 생성
        documents = load_docs() 
        vectorstore = create_vectorstore(documents)

        # RetrievalQA 체인 생성
        qa_chain = create_rag_chain(vectorstore)

        # 예제 질문에 대한 답변 생성
        #question = "강서구 지원정책 알려줘"
        #answer = qa_chain.invoke({"input": question})
        answer = qa_chain.invoke({"input": user_input})

        print("dd")
        

        return answer
    
    except Exception as e:
        print(f"Error fetching response from OpenAI: {e}")
        return "죄송합니다. 현재 서비스를 제공할 수 없습니다. 나중에 다시 시도해 주세요."


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


def load_district_data():
    """JSON 파일에서 구 이름과 URL 데이터를 로드"""
    with open('district_websites.json', 'r', encoding='utf-8') as f:
        district_data = json.load(f)
    return district_data

# 정책 정보 조회
@Chatbot.route('/policy')
class Policy(Resource):
    def post(self):
        """정책 정보 조회"""
        try:
            # JSON 형식으로 사용자 입력 받기
            data = request.get_json()
            district_name = data.get("district_name")

            if not district_name:
                return jsonify({"error": "district_name field is required"}), 400

            # 구 정보 로드
            district_data = load_district_data()
            
            # 입력된 구 이름과 일치하는 구 정보 찾기
            for district in district_data:
                if district["district_name"] == district_name:
                    # 구 이름과 URL을 반환
                    response_message = f"{district_name} 지원 정책 정보입니다."
                    response_url = district["district_url"]
                    
                    # OpenAI API를 통해 대답 생성
                    openai_response = get_response(response_message)
                    
                    return jsonify({
                        "message": openai_response,
                        "district_url": response_url
                    })
            
            # 입력된 구 이름이 목록에 없을 경우
            return jsonify({"error": f"No data found for district: {district_name}"}), 404

        except Exception as e:
            logger.error(f"Error processing policy request: {e}")
            return jsonify({"error": "Internal server error"}), 500



# 파일이 저장될 디렉토리
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 파일 확장자 확인 함수
def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

            # 파일이 없거나 빈 파일인지 확인
            if file.filename == '':
                return jsonify({"message": "파일이 비어 있습니다."}), 400

                        # 파일 확장자 확인
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # 파일을 서버의 임시 디렉터리에 저장
                filepath = os.path.join("/tmp", filename)
                file.save(filepath)
                
                ### 이미지 인식 프로세스를 수행 & 결과 반환.


                # 예시로 객체를 "캔"으로 인식했다고 가정합니다.
                recognized_object = "can"
                message = f"The recognized object is a {recognized_object}. The {recognized_object} is emptied of its contents and discharged without adding any foreign substances."
                
                return jsonify({"message": message})
            else:
                return jsonify({"error": "Invalid file type"}), 400
        
        except Exception as e:
            logger.error(f"Error during file upload: {e}", exc_info=True)  # 에러 로그 추가
            return jsonify({"message": "서버 오류가 발생했습니다.", "error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)