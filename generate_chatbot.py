import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()
# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")
#print(api_key)

# 문서 로드 함수
def load_docs():
    loader = TextLoader('text.txt')
    print(loader)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    return splits


# 벡터 스토어 생성 함수
def create_vectorstore(splits):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectorstore


# RetrievalQA 체인 생성 함수
def create_rag_chain(vectorstore):
    llm = ChatOpenAI(model_name="gpt-4o", temperature=1, openai_api_key=api_key)

    prompt = ChatPromptTemplate.from_template(
    """아래의 문맥을 사용하여 질문에 답하십시오.
    정보가 없는 질문이 나오면 대답을 거절하세요.
    
    당신은 서울시의 재활용 지원 정책에 대한 정보를 제공하는 챗봇입니다. 
    친절하고 정중한 어조로 대답하세요. 한국어로 대답하세요. 당신의 이름은 '서울 ReChat' 입니다. 
    '행정구역' 열에서 해당 지역을 찾아 맞는 정보만 정확하게 읽으세요. 

    번호 단위로 줄바꿈을 하십시오.
    인삿말을 빼고 1번부터 시작하십시오.

    각 지역에 필요한 정보는 여러 행에 존재합니다. 
    먼저 지역을 찾아 연속 5개의 행을 읽어 '행정구역'에서 요청한 지역과 일치하는 정보만 검색합니다.
    답변 작성 시 “**”, “##” 등의 기호를 삭제하세요. 한 항목을 작성한 후 줄바꿈을 시행하세요. 

    마지막에 답변 요약해서 3문장으로 알려줘
    Context: {context}
    Question: {input}
    Answer:""")

    documents = load_docs() 
    embeddings = OpenAIEmbeddings()
    vector = FAISS.from_documents(documents, embeddings)
    retriever = vector.as_retriever()
    document_chain = create_stuff_documents_chain(llm, prompt)
    qa_chain = create_retrieval_chain(retriever, document_chain)

    return qa_chain

