from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage, Document
import pandas as pd

#data = pd.read_csv("./news_chris.csv")
#text_list = data['QA'].tolist()
#documents = [Document(page_content=text) for text in text_list]


# 전역 변수로 Embeddings와 Database 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
database = Chroma(persist_directory="./database", embedding_function=embeddings)
#database.add_documents(documents)

# Chat 모델과 Retriever 초기화
chat = ChatOpenAI(model="gpt-3.5-turbo")
retriever = database.as_retriever(search_kwargs={"k": 3})

# ConversationBufferMemory 초기화
memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="answer", return_messages=True)

# ConversationalRetrievalQA 체인 초기화
qa = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever, memory=memory, return_source_documents=True, output_key="answer")


