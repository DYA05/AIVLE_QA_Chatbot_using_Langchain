from django.contrib import admin
from .models import *
from import_export.admin import ImportExportMixin, ImportMixin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from import_export import resources
from langchain.schema import Document
from import_export.formats.base_formats import CSV
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import django.db.models.signals
import json
import logging
import openai
from django.shortcuts import render, redirect
from django.urls import path
from django.conf import settings

from import_export.results import RowResult
from import_export import resources

from .models import QueryLog, ChromaDB
from django.apps import AppConfig
from .apps import SelfchatgptConfig

models = apps.get_models()

for model in [QueryLog, Topic]:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass

class ini_ChromaDBAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['id','category', 'QA']
    
    def import_action(self, request, *args, **kwargs):     
        result = super().import_action(request, *args, **kwargs)
        
        # result가 TemplateResponse 객체인 경우, 이를 렌더링하여 데이터를 접근할 수 있도록 한다.
        if hasattr(result, 'context_data') and 'result' in result.context_data:
            import_result = result.context_data['result']
            added_count = self.get_new_instance_count(import_result)
        else:
            added_count = 0
        
        if added_count > 0:  # 실제로 임포트가 발생한 경우에만
            ChromaDB.set_last_import_count(added_count)
        
            # process_new_import 함수를 호출하여 유사도 검사 수행
            self.process_new_import(added_count, import_result)
        
        return result

    def get_new_instance_count(self, import_result):
        added_count = 0
        for row in import_result.rows:
            if row.import_type == RowResult.IMPORT_TYPE_NEW:
                added_count += 1
        return added_count
    
    def process_new_import(self, added_count, import_result):
        database = ChromaDB.get_vectorDB()
        
        try:
            latest_id = ChromaDB.objects.latest('id').id
        except ChromaDB.DoesNotExist:
            return
        
        size = ChromaDB.get_last_import_count()
        # latest_id = ChromaDB.objects.latest('id').id

        
        for id in range(latest_id - size, latest_id + 1):
            try:
                tempDB = ChromaDB.objects.get(id=id)
                self.process_document(tempDB, database)  ### 프로세스 문서 함수 호출
            except ChromaDB.DoesNotExist:
                continue

    def process_document(self, tempDB, vectorDB):
        search_result = vectorDB.similarity_search_with_score(tempDB.QA, k=1)
        similarity_score = round(search_result[0][1], 3) if search_result and search_result[0] else 1
        
        if similarity_score >= 0.5:
            metadata = {'category': tempDB.category} if tempDB.category else {'category': 'None'}
            add_doc = [Document(page_content=tempDB.QA, metadata=metadata)]
            vectorDB.add_documents(add_doc)

            processed_doc = ProcessedDocument.objects.create(page_content=tempDB.QA, metadata=metadata)
        else:
            tempDB.delete()


admin.site.register(ChromaDB, ini_ChromaDBAdmin)