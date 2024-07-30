import os
from openai import OpenAI, ChatOpenAI

from langchain_openai import ChatOpenAI

os.environ['OPENAI_API_KEY'] = ''

# model
llm = ChatOpenAI(model="gpt-3.5-turbo")

# chain 실행
result = llm.invoke("족제비는 육식동물인가?")

print(result.content)