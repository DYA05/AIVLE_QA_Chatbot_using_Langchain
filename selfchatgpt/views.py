from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import QueryLog, Topic
from .init_chatmodel import qa, memory, summary
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

import urllib



def get_topics_by_title(name):
    print(Topic.objects.filter(user_name=name).values('title').distinct(), "here we go")
    return Topic.objects.filter(user_name=name).values('title').distinct()


def get_query_logs_by_title(title, session_id):
    topics = Topic.objects.filter(title=title)
    if topics.exists():
        query_logs = QueryLog.objects.filter(id__in=topics.values_list('qa_id', flat=True))
        return query_logs
    return None

@csrf_exempt
def load_chat(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        session_id = request.session.session_key
        memory.clear()  # 메모리 초기화

        if title:
            # title을 통해 QueryLog 조회
            query_logs = get_query_logs_by_title(title, session_id)

            if query_logs:
                # 세션에 chat_history로 저장합니다.
                chat_history = [{'question': log.query, 'response': log.answer} for log in query_logs]
                for log in query_logs :
                    memory.save_context({"question": log.query}, {"answer": log.answer})
                request.session['chat_history'] = chat_history
                return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error'}, status=400)

    return JsonResponse({'status': 'error'}, status=400)




@csrf_exempt
def chat_view(request):
    name = request.GET.get('name', 'Default Name')
    chat_history = request.session.get('chat_history', [])
    
    # 세션 키가 없을 경우 생성
    session_id = generate_session_key_if_missing(request)
    
    if request.method == 'POST':
        question = request.POST.get('question', '')
        if question:
            response = chat(question, name, session_id)
            chat_history.append({'question': question, 'response': response})
            request.session['chat_history'] = chat_history

            # POST 요청 후 템플릿 렌더링
            context = {
                'chat_history': chat_history,
                'name': name,
                'topics': get_topics_by_title(name),
            }
            return JsonResponse({"question": question, "answer": response, "chat_history": chat_history})

    # `name`과 일치하는 모든 `Title` 가져오기
    topics = get_topics_by_title(name)
    
    context = {
        'chat_history': chat_history,
        'name': name,
        'topics': topics,
    }
    return render(request, 'gpt/chatgpt.html', context)

def generate_session_key_if_missing(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key

def save_query_log(name, query, answer):
    query_log = QueryLog.objects.create(username=name, datetime=datetime.now(), query=query, answer=answer)
    query_log.save()
    return query_log

def save_topic(query_log, session_id, name):
    topic = Topic.objects.create(qa_id=query_log, topic_id=session_id, title="Null", user_name=name)
    topic.save()

def chat(query, name, session_id):
    # 기존 채팅 기록을 메모리에 로드
    memory.load_memory_variables({})
    
    # 새로운 질문을 받고 응답을 생성
    result = qa(query)

    # 응답을 메모리에 저장
    memory.save_context({"question": query}, {"answer": result['answer']})

    # QueryLog 및 Topic 저장
    query_log = save_query_log(name, query, result['answer'])
    save_topic(query_log, session_id, name)
    
    return result['answer']

def summary_topic(target):
    chat_history = [{'question': log.query, 'response': log.answer} for log in target]
    return summary(chat_history)



def clear_chat_view(request):
    name = request.GET.get('name', 'Default Name')
    session_id = request.session.session_key
    
    if 'chat_history' in request.session:
        topics = Topic.objects.filter(topic_id=session_id)
        logs = QueryLog.objects.filter(id__in=topics.values_list('qa_id', flat=True))
        
        topics.update(title=summary_topic(logs))

        request.session.flush()  # 세션 데이터 삭제 및 새로운 세션 키 생성
        request.session.create()
    
    memory.clear()  # 메모리 초기화
    
    # URL에 name 값을 포함하여 redirect
    return redirect(reverse('selfchatgpt:chat_view') + f'?name={urllib.parse.quote(name)}')

