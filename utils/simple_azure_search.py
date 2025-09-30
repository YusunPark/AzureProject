"""
간단한 Azure AI Search 문서 관리 서비스
Azure Search 패키지 없이도 작동하는 기본 버전
"""
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import openai
import requests
from config import AZURE_SEARCH_CONFIG, AI_CONFIG

class SimpleAzureSearchService:
    def __init__(self):
        self.available = False
        self.openai_client = None
        self.index_name = "company-documents"
        self.endpoint = None
        self.api_key = None
        self._init_search()
        self._init_openai()
    
    def _init_search(self):
        """Azure Search 초기화 (REST API 사용)"""
        try:
            if AZURE_SEARCH_CONFIG["endpoint"] and AZURE_SEARCH_CONFIG["admin_key"]:
                self.endpoint = AZURE_SEARCH_CONFIG["endpoint"]
                self.api_key = AZURE_SEARCH_CONFIG["admin_key"]
                self.available = True
                print("✅ Azure Search 초기화 성공 (REST API)")
            else:
                print("⚠️ Azure Search 설정이 없습니다.")
                
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
                print("✅ OpenAI 초기화 성공 (임베딩용)")
        except Exception as e:
            print(f"⚠️ OpenAI 초기화 실패: {e}")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """텍스트 임베딩 생성"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model=AI_CONFIG.get("embedding_deployment_name", "text-embedding-3-large"),
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"임베딩 생성 실패: {e}")
            return None
    
    def extract_text_content(self, file_content: bytes, filename: str) -> str:
        """파일에서 텍스트 추출"""
        try:
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'csv']:
                return file_content.decode('utf-8', errors='ignore')
            
            elif file_ext in ['docx']:
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
                return f"지원되지 않는 파일 형식: {filename}"
                
        except Exception as e:
            return f"텍스트 추출 오류: {str(e)}"
    
    def upload_document_to_search(self, file_content: bytes, filename: str, 
                                 file_id: str, blob_url: str, 
                                 metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        문서를 Azure AI Search에 업로드 (REST API 사용)
        """
        if not self.available:
            return {"success": False, "error": "Azure Search 사용 불가"}
        
        try:
            # 텍스트 추출
            content = self.extract_text_content(file_content, filename)
            
            # 요약 생성 (내용이 긴 경우)
            summary = content[:300] + "..." if len(content) > 300 else content
            
            # 키워드 추출
            keywords = self.extract_keywords(content)
            
            # 제목 추출
            title = filename.rsplit('.', 1)[0] if '.' in filename else filename
            
            # 검색 문서 구성
            search_document = {
                "id": f"doc_{file_id}",
                "title": title,
                "content": content,
                "filename": filename,
                "file_id": file_id,
                "document_type": "training",
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "file_size": len(file_content),
                "keywords": keywords,
                "summary": summary,
                "blob_url": blob_url,
                "@search.action": "upload"
            }
            
            # REST API로 문서 업로드
            upload_url = f"{self.endpoint}/indexes/{self.index_name}/docs/index"
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.api_key
            }
            
            payload = {
                "value": [search_document]
            }
            
            response = requests.post(
                upload_url,
                headers=headers,
                json=payload,
                params={'api-version': AZURE_SEARCH_CONFIG.get("api_version", "2020-06-30")}
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "search_doc_id": f"doc_{file_id}",
                    "title": title,
                    "content_length": len(content),
                    "keywords": keywords,
                    "has_embedding": False,
                    "response_status": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"Upload failed: {response.status_code} - {response.text}",
                    "filename": filename
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
        
        import re
        
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
                        use_semantic: bool = False) -> List[Dict[str, Any]]:
        """
        문서 검색 (REST API 사용)
        """
        if not self.available:
            return []
        
        try:
            search_url = f"{self.endpoint}/indexes/{self.index_name}/docs/search"
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.api_key
            }
            
            search_body = {
                "search": query,
                "top": top,
                "count": True
            }
            
            # 필터 추가
            if document_type:
                search_body["filter"] = f"document_type eq '{document_type}'"
            
            response = requests.post(
                search_url,
                headers=headers,
                json=search_body,
                params={'api-version': AZURE_SEARCH_CONFIG.get("api_version", "2020-06-30")}
            )
            
            if response.status_code == 200:
                results = response.json().get('value', [])
                documents = []
                
                for result in results:
                    doc = {
                        "id": result.get("id", ""),
                        "title": result.get("title", "제목 없음"),
                        "content": result.get("content", ""),
                        "filename": result.get("filename", ""),
                        "file_id": result.get("file_id", ""),
                        "document_type": result.get("document_type", "training"),
                        "upload_date": result.get("upload_date", ""),
                        "keywords": result.get("keywords", ""),
                        "summary": result.get("summary", ""),
                        "blob_url": result.get("blob_url", ""),
                        "search_score": result.get("@search.score", 0)
                    }
                    documents.append(doc)
                
                return documents
            elif response.status_code == 404:
                # 인덱스가 존재하지 않는 경우 빈 리스트 반환
                if "not found" in response.text.lower():
                    return []
                else:
                    print(f"검색 실패: {response.status_code} - {response.text}")
                    return []
            else:
                print(f"검색 실패: {response.status_code} - {response.text}")
                return []
            
        except Exception as e:
            print(f"검색 실패: {e}")
            return []
    
    def delete_document(self, search_doc_id: str) -> bool:
        """문서 삭제"""
        if not self.available:
            return False
        
        try:
            delete_url = f"{self.endpoint}/indexes/{self.index_name}/docs/index"
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.api_key
            }
            
            payload = {
                "value": [{
                    "id": search_doc_id,
                    "@search.action": "delete"
                }]
            }
            
            response = requests.post(
                delete_url,
                headers=headers,
                json=payload,
                params={'api-version': AZURE_SEARCH_CONFIG.get("api_version", "2020-06-30")}
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"문서 삭제 실패: {e}")
            return False
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """검색 인덱스 통계"""
        if not self.available:
            return {"available": False}
        
        try:
            # 간단한 통계 조회
            search_results = self.search_documents("*", top=0)
            
            return {
                "available": True,
                "index_name": self.index_name,
                "total_documents": "N/A (REST API 제한)",
                "endpoint": self.endpoint,
                "has_embedding": self.openai_client is not None
            }
            
        except Exception as e:
            return {
                "available": True,
                "error": str(e),
                "index_name": self.index_name
            }
    
    def list_all_documents(self) -> List[Dict[str, Any]]:
        """모든 문서 목록 조회"""
        return self.search_documents("*", top=1000, use_semantic=False)

# 기존 AzureSearchService를 SimpleAzureSearchService로 대체하는 별칭
AzureSearchService = SimpleAzureSearchService