"""
Azure Search 인덱스 설정 및 문서 인덱싱 유틸리티
"""
import json
import requests
import sys
import os
from typing import List, Dict, Any

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AZURE_SEARCH_CONFIG

class AzureSearchSetup:
    def __init__(self):
        self.endpoint = AZURE_SEARCH_CONFIG["endpoint"]
        self.admin_key = AZURE_SEARCH_CONFIG["admin_key"]
        self.index_name = AZURE_SEARCH_CONFIG["index_name"]
        self.api_version = AZURE_SEARCH_CONFIG["api_version"]
        
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': self.admin_key
        }
    
    def create_document_index(self) -> bool:
        """문서 검색용 인덱스 생성"""
        index_schema = {
            "name": self.index_name,
            "fields": [
                {
                    "name": "id",
                    "type": "Edm.String",
                    "key": True,
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True
                },
                {
                    "name": "title",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": False,
                    "retrievable": True
                },
                {
                    "name": "content",
                    "type": "Edm.String", 
                    "searchable": True,
                    "filterable": False,
                    "retrievable": True
                },
                {
                    "name": "summary",
                    "type": "Edm.String",
                    "searchable": True,
                    "filterable": False,
                    "retrievable": True
                },
                {
                    "name": "source",
                    "type": "Edm.String",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True
                },
                {
                    "name": "keywords",
                    "type": "Collection(Edm.String)",
                    "searchable": True,
                    "filterable": True,
                    "retrievable": True
                },
                {
                    "name": "created_at",
                    "type": "Edm.DateTimeOffset",
                    "searchable": False,
                    "filterable": True,
                    "sortable": True,
                    "retrievable": True
                },
                {
                    "name": "document_type",
                    "type": "Edm.String",
                    "searchable": False,
                    "filterable": True,
                    "retrievable": True
                }
            ],
            "scoringProfiles": [
                {
                    "name": "relevance-boost",
                    "text": {
                        "weights": {
                            "title": 3.0,
                            "summary": 2.0,
                            "content": 1.5,
                            "keywords": 2.5
                        }
                    }
                }
            ],
            "corsOptions": {
                "allowedOrigins": ["*"],
                "maxAgeInSeconds": 60
            }
        }
        
        try:
            url = f"{self.endpoint}/indexes/{self.index_name}"
            params = {'api-version': self.api_version}
            
            response = requests.put(url, headers=self.headers, json=index_schema, params=params)
            
            if response.status_code in [200, 201]:
                print(f"✅ 인덱스 '{self.index_name}' 생성 성공")
                return True
            else:
                print(f"❌ 인덱스 생성 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 인덱스 생성 오류: {e}")
            return False
    
    def upload_sample_documents(self) -> bool:
        """샘플 문서들을 인덱스에 업로드"""
        try:
            # 로컬 샘플 데이터 로드
            with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get("documents", [])
            
            # Azure Search 형식으로 변환
            upload_docs = []
            for doc in documents:
                upload_doc = {
                    "@search.action": "upload",
                    "id": str(doc.get("id", "")),
                    "title": doc.get("title", ""),
                    "content": doc.get("content", ""),
                    "summary": doc.get("summary", ""),
                    "source": doc.get("source", ""),
                    "keywords": doc.get("keywords", []),
                    "created_at": doc.get("created_at", "2024-01-01T00:00:00Z"),
                    "document_type": doc.get("file_type", "docx")
                }
                upload_docs.append(upload_doc)
            
            # 문서 업로드
            upload_payload = {"value": upload_docs}
            
            url = f"{self.endpoint}/indexes/{self.index_name}/docs/index"
            params = {'api-version': self.api_version}
            
            response = requests.post(url, headers=self.headers, json=upload_payload, params=params)
            
            if response.status_code in [200, 207]:
                result = response.json()
                successful_uploads = len([r for r in result.get('value', []) if r.get('status')])
                print(f"✅ 문서 업로드 성공: {successful_uploads}개")
                return True
            else:
                print(f"❌ 문서 업로드 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 문서 업로드 오류: {e}")
            return False
    
    def setup_complete_search_service(self) -> bool:
        """완전한 검색 서비스 설정"""
        print("🚀 Azure Search 서비스 설정 시작...")
        
        # 1. 인덱스 생성
        if self.create_document_index():
            print("⏳ 인덱스 생성 완료, 문서 업로드 중...")
            
            # 2. 샘플 문서 업로드  
            if self.upload_sample_documents():
                print("✅ Azure Search 서비스 설정 완료!")
                print(f"📊 인덱스명: {self.index_name}")
                print(f"🔍 검색 엔드포인트: {self.endpoint}")
                return True
        
        return False

if __name__ == "__main__":
    # 설정 실행
    setup = AzureSearchSetup()
    setup.setup_complete_search_service()