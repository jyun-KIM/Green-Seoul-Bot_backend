# Green Seoul Bot 프로젝트

**Green Seoul Bot**은 서울시 25개 자치구의 재활용 정책 정보 및 대형 폐기물 처리 방법을 제공하는 챗봇입니다. OpenAI의 GPT-4 API, LangChain, YOLO 모델을 활용하여 친환경 정책과 폐기물 처리에 대한 사용자 친화적인 응답을 제공합니다.

---

## **주요 기능**

1. **재활용 지원 정책 정보 제공**
   - 자치구별 재활용 지원 정책을 조회하고 요약된 정보를 제공합니다.
   - 서울시 25개 자치구를 지원합니다.
   - LangChain 기반 벡터 검색을 통해 정확한 정보 제공.

2. **대형 폐기물 처리 가이드**
   - 대형 폐기물 항목별 처리 방법 제공.
   - 사용자 업로드 이미지를 YOLO 모델로 분류하여 처리 방식을 안내.
   - 해당 구청 홈페이지로 바로 연결하여 간편한 등록 지원.

3. **사용자 친화적 인터페이스**
   - 자연어를 통해 한국어로 질의 및 응답 가능.
   - 정중하고 명확한 답변 제공, Green Seoul Bot의 친근한 챗봇 캐릭터 유지.

---

## **기술 스택**

- **백엔드**
  - Flask: 경량 웹 프레임워크.
  - Flask-RESTx: RESTful API와 Swagger 문서 생성.

- **AI 및 머신러닝**
  - **OpenAI GPT-4**: 텍스트 기반 응답 생성.
  - **YOLO 모델**: 대형 폐기물 이미지 분류.

- **LangChain**
  - 정책 데이터를 로드 및 벡터 스토어로 관리.
  - FAISS 기반 벡터 검색.
  - RetrievalQA 체인을 통해 문맥 기반 질문 응답.

- **데이터베이스**
  - JSON 파일로 정책 및 자치구별 URL 데이터 관리.

---

## **API 엔드포인트**

### **챗봇 관련 엔드포인트**

#### 1. **Green Seoul Bot과 대화**
- **URL**: `/chatbot/chat`
- **Method**: POST
- **요청 예시**:
  ```json
  {
      "user_input": "재활용 지원 정책 알려줘."
  }
