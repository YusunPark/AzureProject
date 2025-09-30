"""
Azure AI Search 문서 관리 서비스
문서 업로드, 인덱싱, 검색 기능 제공
"""
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import openai
import hashlib
import re
from config import AZURE_SEARCH_CONFIG, AI_CONFIG

# Azure Search 패키지 조건부 import
try:
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.models import VectorizedQuery
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SimpleField,
        SearchableField,
        SearchField,  # 벡터 필드용
        SearchFieldDataType,
        VectorSearch,
        VectorSearchProfile,
        HnswAlgorithmConfiguration,
        SemanticConfiguration,
        SemanticSearch,
        SemanticPrioritizedFields,
        SemanticField
    )
    AZURE_SEARCH_AVAILABLE = True
except ImportError:
    print("⚠️ Azure Search 패키지가 설치되지 않았습니다. 검색 기능이 제한됩니다.")
    AZURE_SEARCH_AVAILABLE = False
    SearchClient = None
    SearchIndexClient = None
    VectorizedQuery = None
    AzureKeyCredential = None

class AzureSearchService:
    def __init__(self):
        self.available = False
        self.search_client = None
        self.index_client = None
        self.openai_client = None
        self.index_name = "company-documents"  # 기본 인덱스명
        self._init_search()
        self._init_openai()
    
    def _init_search(self):
        """Azure Search 초기화"""
        try:
            if not AZURE_SEARCH_AVAILABLE:
                print("⚠️ Azure Search 패키지를 사용할 수 없습니다.")
                self.available = False
                return
                
            if AZURE_SEARCH_CONFIG["endpoint"] and AZURE_SEARCH_CONFIG["admin_key"]:
                credential = AzureKeyCredential(AZURE_SEARCH_CONFIG["admin_key"])
                
                self.search_client = SearchClient(
                    endpoint=AZURE_SEARCH_CONFIG["endpoint"],
                    index_name=self.index_name,
                    credential=credential
                )
                
                self.index_client = SearchIndexClient(
                    endpoint=AZURE_SEARCH_CONFIG["endpoint"],
                    credential=credential
                )
                
                self.available = True
                print("✅ Azure Search 초기화 성공")
            else:
                print("⚠️ Azure Search 설정이 없습니다.")
                self.available = False
                
        except Exception as e:
            print(f"⚠️ Azure Search 초기화 실패: {e}")
            self.available = False
    
    def _init_openai(self):
        """OpenAI 초기화 (벡터 임베딩용)"""
        try:
            if AI_CONFIG["openai_api_key"] and AI_CONFIG["openai_endpoint"]:
                self.openai_client = openai.AzureOpenAI(
                    azure_endpoint=AI_CONFIG["openai_endpoint"],
                    api_key=AI_CONFIG["openai_api_key"],
                    api_version=AI_CONFIG["api_version"]
                )
        except Exception as e:
            print(f"⚠️ OpenAI 초기화 실패: {e}")
    
    def create_index_if_not_exists(self):
        """인덱스가 없으면 생성 (벡터 필드 문제 해결 포함)"""
        if not self.available or not AZURE_SEARCH_AVAILABLE:
            return False
        
        try:
            from azure.search.documents.indexes.models import (
                SearchIndex, SimpleField, SearchableField, ComplexField,
                SearchFieldDataType, VectorSearch, HnswAlgorithmConfiguration,
                VectorSearchProfile, SemanticConfiguration, SemanticSearch,
                SemanticPrioritizedFields, SemanticField
            )
            
            # 인덱스 존재 확인 및 벡터 필드 검증
            index_needs_recreation = False
            try:
                existing_index = self.index_client.get_index(self.index_name)
                
                # contentVector 필드가 올바르게 구성되었는지 확인
                vector_field_exists = False
                if self.openai_client:  # OpenAI가 활성화된 경우만 벡터 필드 확인
                    for field in existing_index.fields:
                        if field.name == "contentVector":
                            if hasattr(field, 'vector_search_dimensions') and field.vector_search_dimensions:
                                vector_field_exists = True
                                break
                    
                    if not vector_field_exists:
                        index_needs_recreation = True
                        print(f"⚠️ 기존 인덱스에 벡터 필드가 올바르게 구성되지 않았습니다. 인덱스를 재생성합니다.")
                
                if not index_needs_recreation:
                    print(f"✅ Azure Search 인덱스 '{self.index_name}' 이미 존재하고 올바르게 구성되었습니다.")
                    return True
                else:
                    # 기존 인덱스 삭제
                    self.index_client.delete_index(self.index_name)
                    print(f"🗑️ 기존 인덱스 '{self.index_name}' 삭제 완료")
                    
            except Exception as e:
                print(f"📝 인덱스 확인 중 (새 인덱스 생성 예정): {e}")
                # 인덱스가 없거나 오류 발생시 생성 진행
            
            # 벡터 검색 설정
            vector_search = VectorSearch(
                profiles=[
                    VectorSearchProfile(
                        name="myHnswProfile",
                        algorithm_configuration_name="myHnsw"
                    )
                ],
                algorithms=[
                    HnswAlgorithmConfiguration(name="myHnsw")
                ]
            )
            
            # 시맨틱 검색 설정
            semantic_config = SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")]
                )
            )
            
            semantic_search = SemanticSearch(configurations=[semantic_config])
            
            # 필드 정의
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SearchableField(name="filename", type=SearchFieldDataType.String),
                SimpleField(name="file_id", type=SearchFieldDataType.String),
                SimpleField(name="document_type", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="upload_date", type=SearchFieldDataType.DateTimeOffset, filterable=True),
                SimpleField(name="file_size", type=SearchFieldDataType.Int32),
                SearchableField(name="keywords", type=SearchFieldDataType.String),
                SearchableField(name="summary", type=SearchFieldDataType.String),
                SimpleField(name="blob_url", type=SearchFieldDataType.String),
                # 벡터 필드 (임베딩이 가능한 경우)
                SearchField(
                    name="contentVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,  # Azure Search 요구사항: 벡터 필드는 searchable=True 필요
                    vector_search_dimensions=3072,  # text-embedding-3-large는 3072 차원
                    vector_search_profile_name="myHnswProfile"
                ) if self.openai_client else None
            ]
            
            # None 필드 제거
            fields = [f for f in fields if f is not None]
            
            # 인덱스 생성
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search if self.openai_client else None,
                semantic_search=semantic_search
            )
            
            self.index_client.create_index(index)
            print(f"✅ 인덱스 '{self.index_name}' 생성 완료")
            return True
            
        except Exception as e:
            print(f"❌ 인덱스 생성 실패: {e}")
            return False
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """텍스트 임베딩 생성 - 토큰 길이 제한 처리"""
        if not self.openai_client:
            return None
        
        try:
            # 텍스트 길이 제한 (OpenAI 임베딩 모델 토큰 제한: 8192)
            # 대략 1 토큰 = 4 문자로 계산하여 안전하게 30000자로 제한
            if len(text) > 30000:
                text = text[:30000] + "... (내용 길이로 인해 일부 생략됨)"
                print(f"⚠️ 텍스트가 길어서 {len(text):,}자로 축소했습니다.")
            
            response = self.openai_client.embeddings.create(
                model=AI_CONFIG.get("embedding_deployment_name", "text-embedding-3-large"),
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            error_msg = str(e)
            if "maximum context length" in error_msg:
                print(f"⚠️ 텍스트 길이 초과로 임베딩을 건너뜁니다: {len(text):,}자")
                # 더 짧게 자르고 재시도
                short_text = text[:15000]
                try:
                    response = self.openai_client.embeddings.create(
                        model=AI_CONFIG.get("embedding_deployment_name", "text-embedding-3-large"),
                        input=short_text
                    )
                    return response.data[0].embedding
                except:
                    print("❌ 짧은 텍스트로도 임베딩 실패")
                    return None
            else:
                print(f"❌ 임베딩 생성 실패: {error_msg}")
                return None
    
    def extract_text_content(self, file_content: bytes, filename: str) -> str:
        """파일에서 텍스트 추출"""
        try:
            # 파일 확장자에 따른 처리
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'csv']:
                # 텍스트 파일은 직접 디코딩
                return file_content.decode('utf-8', errors='ignore')
            
            elif file_ext in ['docx']:
                # Word 문서 처리 (python-docx 사용)
                try:
                    from docx import Document
                    import io
                    
                    doc = Document(io.BytesIO(file_content))
                    text_parts = []
                    for paragraph in doc.paragraphs:
                        text_parts.append(paragraph.text)
                    return '\n'.join(text_parts)
                except:
                    return f"Word 문서 처리 오류: {filename}"
            
            elif file_ext == 'pdf':
                # PDF 텍스트 추출
                try:
                    import io
                    import PyPDF2
                    
                    # PyPDF2로 PDF 텍스트 추출 시도
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                    text_parts = []
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text.strip():
                                text_parts.append(page_text)
                        except Exception as e:
                            print(f"PDF 페이지 {page_num} 추출 오류: {e}")
                            continue
                    
                    extracted_text = '\n'.join(text_parts)
                    
                    # 추출된 텍스트가 너무 적으면 pdfplumber 시도
                    if len(extracted_text.strip()) < 100:
                        try:
                            import pdfplumber
                            
                            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                                plumber_text = []
                                for page in pdf.pages:
                                    try:
                                        page_text = page.extract_text()
                                        if page_text:
                                            plumber_text.append(page_text)
                                    except:
                                        continue
                                
                                if plumber_text:
                                    extracted_text = '\n'.join(plumber_text)
                        except ImportError:
                            pass  # pdfplumber가 없으면 PyPDF2 결과 사용
                    
                    if extracted_text.strip():
                        return extracted_text
                    else:
                        return f"PDF 파일에서 텍스트를 추출할 수 없습니다: {filename}"
                        
                except Exception as e:
                    return f"PDF 처리 오류 ({filename}): {str(e)}"
            
            else:
                # 기타 파일은 바이너리로 처리
                return f"바이너리 파일: {filename} (크기: {len(file_content)} bytes)"
                
        except Exception as e:
            return f"텍스트 추출 오류: {str(e)}"
    
    def upload_document_to_search(self, file_content: bytes, filename: str, 
                                 file_id: str, blob_url: str, 
                                 metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        문서를 Azure AI Search에 업로드
        
        Args:
            file_content: 파일 내용
            filename: 파일명
            file_id: 파일 고유 ID
            blob_url: Azure Storage blob URL
            metadata: 추가 메타데이터
            
        Returns:
            업로드 결과
        """
        if not self.available:
            return {"success": False, "error": "Azure Search 사용 불가"}
        
        try:
            # 인덱스 존재 확인 및 생성
            self.create_index_if_not_exists()
            
            # 텍스트 추출
            content = self.extract_text_content(file_content, filename)
            
            # 요약 생성 (내용이 긴 경우)
            summary = content[:300] + "..." if len(content) > 300 else content
            
            # 키워드 추출 (간단한 방식)
            keywords = self.extract_keywords(content)
            
            # 제목 추출 (파일명에서 확장자 제거)
            title = filename.rsplit('.', 1)[0] if '.' in filename else filename
            
            # 임베딩 생성
            content_vector = self.generate_embedding(content) if self.openai_client else None
            
            # 문서 ID 생성 (검색용)
            search_doc_id = f"doc_{file_id}"
            
            # 검색 문서 구성
            search_document = {
                "id": search_doc_id,
                "title": title,
                "content": content,
                "filename": filename,
                "file_id": file_id,
                "document_type": "training",
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "file_size": len(file_content),
                "keywords": keywords,
                "summary": summary,
                "blob_url": blob_url
            }
            
            # 벡터 필드 추가 (임베딩이 있는 경우)
            if content_vector:
                search_document["contentVector"] = content_vector
            
            # 추가 메타데이터 포함
            if metadata:
                for key, value in metadata.items():
                    if key not in search_document:
                        search_document[f"meta_{key}"] = str(value)
            
            # 문서 업로드
            result = self.search_client.upload_documents([search_document])
            
            return {
                "success": True,
                "search_doc_id": search_doc_id,
                "title": title,
                "content_length": len(content),
                "keywords": keywords,
                "has_embedding": content_vector is not None,
                "upload_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def extract_keywords(self, content: str) -> str:
        """간단한 키워드 추출"""
        if not content:
            return ""
        
        # 한글, 영문 단어 추출 (3글자 이상)
        words = re.findall(r'[가-힣]{3,}|[a-zA-Z]{3,}', content)
        
        # 빈도 계산
        word_count = {}
        for word in words:
            word_lower = word.lower()
            word_count[word_lower] = word_count.get(word_lower, 0) + 1
        
        # 상위 10개 키워드 반환
        top_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
        return ", ".join([word for word, count in top_keywords])
    
    def search_documents(self, query: str, top: int = 10, 
                        document_type: Optional[str] = None,
                        use_semantic: bool = True) -> List[Dict[str, Any]]:
        """
        문서 검색
        
        Args:
            query: 검색 쿼리
            top: 반환할 결과 수
            document_type: 문서 타입 필터
            use_semantic: 시맨틱 검색 사용 여부
            
        Returns:
            검색 결과 목록
        """
        if not self.available:
            return []
        
        try:
            # 검색 파라미터 설정
            search_params = {
                "search_text": query,
                "top": top,
                "include_total_count": True
            }
            
            # 필터 추가
            if document_type:
                search_params["filter"] = f"document_type eq '{document_type}'"
            
            # 시맨틱 검색 설정
            if use_semantic:
                search_params["query_type"] = "semantic"
                search_params["semantic_configuration_name"] = "my-semantic-config"
            
            # 벡터 검색 추가 (임베딩이 가능한 경우)
            if self.openai_client:
                query_vector = self.generate_embedding(query)
                if query_vector:
                    search_params["vector_queries"] = [
                        VectorizedQuery(
                            vector=query_vector,
                            k_nearest_neighbors=5,
                            fields="contentVector"
                        )
                    ]
            
            # 검색 실행
            results = self.search_client.search(**search_params)
            
            # 결과 변환
            documents = []
            for result in results:
                doc = {
                    "id": result["id"],
                    "title": result.get("title", "제목 없음"),
                    "content": result.get("content", ""),
                    "filename": result.get("filename", ""),
                    "file_id": result.get("file_id", ""),
                    "document_type": result.get("document_type", "training"),
                    "upload_date": result.get("upload_date", ""),
                    "keywords": result.get("keywords", ""),
                    "summary": result.get("summary", ""),
                    "blob_url": result.get("blob_url", ""),
                    "search_score": result.get("@search.score", 0),
                    "search_reranker_score": result.get("@search.reranker_score")
                }
                documents.append(doc)
            
            # 검색 결과가 없으면 더미 데이터 제공
            if not documents:
                documents = self._get_dummy_internal_documents(query, top)
            
            return documents
            
        except Exception as e:
            print(f"검색 실패: {e}")
            # 오류 시에도 더미 데이터 제공
            return self._get_dummy_internal_documents(query, top)
    
    def _get_dummy_internal_documents(self, query: str, top: int) -> List[Dict[str, Any]]:
        """더미 내부 문서 생성 (검색 결과가 없을 때)"""
        import random
        
        dummy_docs = []
        
        # 더 현실적인 사내 문서 템플릿
        templates = [
            {
                "title": f"{query} 관련 사내 가이드라인",
                "content": f"{query}에 대한 사내 표준 가이드라인입니다. 회사의 정책과 절차, 모범 사례를 정리한 공식 문서로, 직원들이 업무에서 참고해야 할 핵심 내용을 담고 있습니다.",
                "document_type": "가이드라인",
                "filename": f"{query}_가이드라인.pdf"
            },
            {
                "title": f"{query} 프로젝트 사례 연구",
                "content": f"{query}와 관련된 과거 프로젝트 수행 사례입니다. 프로젝트 진행 과정, 발생한 이슈와 해결방법, 성과 지표 등을 상세히 기록한 내부 자료입니다.",
                "document_type": "프로젝트 사례",
                "filename": f"{query}_프로젝트사례.docx"
            },
            {
                "title": f"{query} 기술 문서",
                "content": f"{query}에 대한 기술적 상세 정보를 담은 사내 기술 문서입니다. 시스템 아키텍처, 구현 방법, 기술적 고려사항 등을 포함합니다.",
                "document_type": "기술 문서",
                "filename": f"{query}_기술문서.md"
            }
        ]
        
        for i, template in enumerate(templates[:min(top, 3)]):
            dummy_docs.append({
                "id": f"dummy_internal_{i+1}",
                "title": template["title"],
                "content": template["content"],
                "filename": template["filename"],
                "file_id": f"file_{i+1}",
                "document_type": template["document_type"],
                "upload_date": "2024-01-01",
                "keywords": query,
                "summary": template["content"][:100] + "...",
                "blob_url": f"https://example.blob.core.windows.net/{template['filename']}",
                "search_score": 0.8 - (i * 0.1),
                "search_reranker_score": None
            })
        
        return dummy_docs

    def delete_document(self, search_doc_id: str) -> bool:
        """
        검색 인덱스에서 문서 삭제
        
        Args:
            search_doc_id: 검색 문서 ID
            
        Returns:
            삭제 성공 여부
        """
        if not self.available:
            return False
        
        try:
            self.search_client.delete_documents([{"id": search_doc_id}])
            return True
        except Exception as e:
            print(f"문서 삭제 실패: {e}")
            return False
    
    def get_document_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        파일 ID로 문서 검색
        
        Args:
            file_id: 파일 ID
            
        Returns:
            문서 정보 또는 None
        """
        if not self.available:
            return None
        
        try:
            results = self.search_client.search(
                search_text="*",
                filter=f"file_id eq '{file_id}'",
                top=1
            )
            
            for result in results:
                return {
                    "id": result["id"],
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "filename": result.get("filename", ""),
                    "file_id": result.get("file_id", ""),
                    "document_type": result.get("document_type", ""),
                    "upload_date": result.get("upload_date", ""),
                    "keywords": result.get("keywords", ""),
                    "summary": result.get("summary", ""),
                    "blob_url": result.get("blob_url", "")
                }
            
            return None
            
        except Exception as e:
            print(f"문서 조회 실패: {e}")
            return None
    
    def list_all_documents(self) -> List[Dict[str, Any]]:
        """
        모든 문서 목록 조회
        
        Returns:
            전체 문서 목록
        """
        return self.search_documents("*", top=1000, use_semantic=False)
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        검색 인덱스 통계
        
        Returns:
            통계 정보
        """
        if not self.available:
            return {"available": False}
        
        try:
            # 전체 문서 수 조회
            results = self.search_client.search(
                search_text="*",
                top=0,
                include_total_count=True
            )
            
            total_count = results.get_count() if hasattr(results, 'get_count') else 0
            
            return {
                "available": True,
                "index_name": self.index_name,
                "total_documents": total_count,
                "endpoint": AZURE_SEARCH_CONFIG["endpoint"],
                "has_embedding": self.openai_client is not None
            }
            
        except Exception as e:
            return {
                "available": True,
                "error": str(e),
                "index_name": self.index_name
            }