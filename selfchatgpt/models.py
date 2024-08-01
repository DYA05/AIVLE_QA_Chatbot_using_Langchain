from django.db import models
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores import Chroma
from django.utils import timezone
from import_export import resources
from import_export.results import RowResult
import logging
import django.db.models.signals
from django.apps import AppConfig
from .apps import SelfchatgptConfig

class QueryLog(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=False)
    datetime = models.DateTimeField(null=False)
    query = models.TextField(null=False)
    answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"QueryLog {self.id} by {self.username}"


class Topic(models.Model):
    qa_id = models.ForeignKey(QueryLog, on_delete=models.CASCADE, db_column='qa_id')
    user_name = models.CharField(max_length=255, null=True)
    topic_id = models.CharField(max_length=100, null=False)
    title = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.topic_id


class ChromaDB(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=256, default='None', null=True)
    QA = models.CharField(max_length=256)

    _last_import_count = 0  # 클래스 변수로 임포트된 데이터 수를 저장

    @classmethod
    def set_last_import_count(cls, count):
        cls._last_import_count = count

    @classmethod
    def get_last_import_count(cls):
        return cls._last_import_count

    @classmethod
    def get_vectorDB(cls):
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        database = Chroma(persist_directory="./database",  # 경로 지정(현 위치에서 db 폴더 생성)
                        embedding_function = embeddings  # 임베딩 벡터로 만들 모델 지정
                        )
        return database
    
    def __str__(self):
        return f"{self.category}: {self.QA}"
    
    @staticmethod
    def add_initial_data(sender, **kwargs):
        ChromaDB.objects.all().delete()
        logger.info("START NEW STEP!!")  ### 로그 추가
        
        database = ChromaDB.get_vectorDB()
        vectorDB = database.get()
        
        documents = vectorDB['documents']
        metadatas = vectorDB['metadatas']

        for i in range(len(documents)):
            category = metadatas[i]['category'] if metadatas[i] and 'category' in metadatas[i] else 'None'
            ChromaDB.objects.create(category=category, QA=documents[i])
