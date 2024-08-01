from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django import forms
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory , ChatMessageHistory 
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


from .init_chatmodel import qa, memory
import pandas as pd
import json


def chat(query, chat_history):
    # 기존 채팅 기록을 메모리에 로드
    
    result = qa(query)

    # 응답을 가져옴
    memory.save_context({"question": query},
        {"answer": result['answer']})

    return result['answer']

@csrf_exempt
def chat_view(request):
    chat_history = request.session.get('chat_history', [])
    if request.method == 'POST':
        question = request.POST.get('question', '')
        if question:
            response = chat(question, chat_history)  # 실제로 ChatGPT API를 호출하여 응답을 받아야 합니다.
            chat_history.append({'question': question, 'response': response})
            request.session['chat_history'] = chat_history
            return JsonResponse({"question": question, "answer": response, "chat_history": chat_history})

    context = {
        'chat_history': chat_history,
    }
    return render(request, 'gpt/chatgpt.html', context)

def clear_chat_view(request):
    if 'chat_history' in request.session:
        del request.session['chat_history']
    memory.clear() # 메모리 초기화
    return redirect('chatgpt:chat_view')