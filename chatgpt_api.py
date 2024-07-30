import os
from openai import OpenAI, ChatOpenAI

from langchain_openai import ChatOpenAI

os.environ['OPENAI_API_KEY'] = 'sk-None-pD8etc7uK3XipaEg9w3qT3BlbkFJc5vO6cFltlMTN2xUgryQ'

# model
llm = ChatOpenAI(model="gpt-3.5-turbo")

# chain 실행
result = llm.invoke("족제비는 육식동물인가?")

print(result.content)