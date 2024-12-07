import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain


# OpenMP 라이브러리의 중복 초기화 허용
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv("OPENAI_API_KEY")

# 문서 로드 함수
def load_rewardPolicy():
    loader = TextLoader('rewardPolicy.txt')
    print(loader)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    return splits


# 정책정보 로드 함수
def load_largewastePolicy():
    loader = TextLoader('largewastePolicy.txt')
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
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    return vectorstore


# 정책정보 체인 생성 함수
def rewardChain(vectorstore):
    llm = ChatOpenAI(model_name="gpt-4o", temperature=1, openai_api_key=api_key)

    prompt = ChatPromptTemplate.from_template(
    """아래의 문맥을 사용하여 질문에 답하십시오.
    
    당신은 서울시의 재활용 지원 정책에 대한 정보를 제공하는 챗봇입니다. 
    친절하고 정중한 어조로 대답하세요. 한국어로 대답하세요. 당신의 이름은 'Green Seoul Bot' 입니다. 
    '행정구역' 열에서 해당 지역을 찾아 맞는 정보만 정확하게 읽으세요. 
    정보를 전달할 때는 인삿말을 넣지 마십시오.

    번호 단위로 줄바꿈을 하십시오.
    인삿말을 빼고 시작하십시오.

    정보를 생성할 때는 정중하고 친절한 챗봇처럼 답변하십시오.

    각 지역에 필요한 정보는 여러 행에 존재합니다. 
    먼저 지역을 찾아 '행정구역'에서 요청한 지역과 일치하는 정보만 검색합니다.
    한 항목을 작성한 후 줄바꿈을 시행하세요. 

    Context: {context}
    Question: {input}
    Answer:""")

    documents = load_rewardPolicy() 
    embeddings = OpenAIEmbeddings()
    vector = FAISS.from_documents(documents, embeddings)
    retriever = vector.as_retriever()
    document_chain = create_stuff_documents_chain(llm, prompt)
    qa_chain = create_retrieval_chain(retriever, document_chain)

    return qa_chain

# 대형폐기물 체인 생성 함수
def largewastChain(vectorstore):
    llm = ChatOpenAI(model_name="gpt-4o", temperature=1, openai_api_key=api_key)

    prompt = ChatPromptTemplate.from_template(
    """아래의 문맥을 사용하여 질문에 답하십시오.
    
    당신은 서울시 대형퍠기물 처리에 대한 정보를 제공하는 챗봇입니다. 
    맨 앞에 인삿말을 넣지 마십시오.
    친절하고 정중한 어조로 대답하세요. 한국어로 대답하세요. 당신의 이름은 'Green Seoul Bot' 입니다. 
    해당 지역을 찾아 정보를 정확하게 읽어오십시오. 

    인삿말을 빼고 시작하십시오.


    Context: {context}
    Question: {input}
    Answer:""")

    documents = load_largewastePolicy() 
    embeddings = OpenAIEmbeddings()
    vector = FAISS.from_documents(documents, embeddings)
    retriever = vector.as_retriever()
    document_chain = create_stuff_documents_chain(llm, prompt)
    qa_chain = create_retrieval_chain(retriever, document_chain)

    return qa_chain
