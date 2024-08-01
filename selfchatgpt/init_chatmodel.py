from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage, Document
from django.urls import reverse
from langchain.prompts import PromptTemplate

import urllib
import pandas as pd
import openai

# 데이터 로드 (필요시)
# data = pd.read_csv("./news_chris.csv")
# text_list = data['QA'].tolist()
# documents = [Document(page_content=text) for text in text_list]

# 전역 변수로 Embeddings와 Database 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
database = Chroma(persist_directory="./database", embedding_function=embeddings)
# database.add_documents(documents)

# Chat 모델과 Retriever 초기화
chat = ChatOpenAI(model="gpt-3.5-turbo")
retriever = database.as_retriever(search_kwargs={"k": 3})

# ConversationBufferMemory 초기화
memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="answer", return_messages=True)

system_instruction = "에이블스쿨과 관련된 질문을 받아주는 고양이 로봇입니다. '~냥'으로만 대답해"
template = (
    f"{system_instruction} "
    "Context와 Chat History도 고려하여 Question을 답해주세요.\n"
    "질문에 대한 답을 모르면, ktaivle@kt.com로 문의해달라고 안내해주세요.\n"
    "질문이 아닌 경우에는, 어떻게 도와드릴 수 있는지 물어봐주세요.\n"
    "----------------------\n"
    "Context: {context}\n\n"
    "Chat History: {chat_history}\n\n"
    "Question: {question}"
)   
prompt = PromptTemplate(
    input_variables=["chat_history", "question", "context"], template=template
)


# ConversationalRetrievalQA 체인 초기화
qa = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever, memory=memory, return_source_documents=True, output_key="answer",
                                           combine_docs_chain_kwargs={"prompt": prompt})




def summary(chat_history):
    talk = ""
    for qa in chat_history:
        talk += '질문 : ' + qa['question'] + '\n'
        talk += '대답 : ' + qa['response'] + '\n'
        
    # # API를 사용하여 'gpt-3.5-turbo' 모델로부터 응답을 생성합니다.
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "다음의 대화의 가장 중요한 키워드를 3개 이하로 알려주고 '핵심 키워드 : 키워드 1, 키워드2' 양식으로 알려줘"},  # 기본 역할 부여
            {"role": "user", "content": talk},
        ]
    )

    return response.choices[0].message.content


'''



connection_manager = ChromaDBConnectionManager()
db_config = {
    "embedding_function": OpenAIEmbeddings(model="text-embedding-ada-002"),
    "client_settings": chromadb.config.Settings(
        anonymized_telemetry=False,
        is_persistent=True,
        persist_directory=settings.CHROMADB_PATH,
    ),
}

# 프롬프트 작성
system_instruction = "KT 에이블스쿨을 위한 챗봇입니다."
template = (
    f"{system_instruction} "
    "Context와 Chat History도 고려하여 Question을 답해주세요.\n"
    "질문에 대한 답을 모르면, ktaivle@kt.com로 문의해달라고 안내해주세요.\n"
    "질문이 아닌 경우에는, 어떻게 도와드릴 수 있는지 물어봐주세요.\n"
    "----------------------\n"
    "Context: {context}\n\n"
    "Chat History: {chat_history}\n\n"
    "Question: {question}"
)
prompt = PromptTemplate(
    input_variables=["chat_history", "question", "context"], template=template
)


def index(request):
    session_key = get_session_key(request)
    chat_message_history = SQLChatMessageHistory(
        session_id=session_key, connection_string=settings.CHAT_MESSAGE_HISTORY_DB_NAME
    )
    messages = chat_message_history.messages
    return render(
        request,
        "selfchatgpt/index.html",
        {"messages": messages},
    )


def chatbot(request):
    if request.method == "POST":
        session_key = get_session_key(request)
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message")
        database = connection_manager.get_connection("aivle_faq", **db_config)
        chat_message_history = SQLChatMessageHistory(
            session_id=session_key,
            connection_string=settings.CHAT_MESSAGE_HISTORY_DB_NAME,
        )
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        retriever = database.as_retriever(search_kwargs={"k": 3})
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=chat_message_history,
            input_key="question",
            output_key="answer",
            return_messages=True,
            k=10,
        )
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            output_key="answer",
            combine_docs_chain_kwargs={"prompt": prompt},
        )
        result = qa({"question": user_message})
        bot_response = result["answer"]
        ChatHistory.objects.create(
            question=user_message,
            answer=bot_response,
        )
        return JsonResponse({"response": bot_response})
    session_key = get_session_key(request)
    chat_message_history = SQLChatMessageHistory(
        session_id=session_key, connection_string=settings.CHAT_MESSAGE_HISTORY_DB_NAME
    )
    messages = chat_message_history.messages
    return render(
        request,
        "selfchatgpt/aivle-bot.html",
        {"messages": messages},
    )
'''