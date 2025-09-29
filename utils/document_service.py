"""
문서 서비스 모듈 - OnlyOffice 연동 및 문서 처리
"""
import json
import requests
import hashlib
import time
from typing import Dict, Any, List
import streamlit as st
from config import ONLYOFFICE_CONFIG

class DocumentService:
    def __init__(self):
        self.docspace_url = ONLYOFFICE_CONFIG["docspace_url"]
        self.sdk_url = ONLYOFFICE_CONFIG["sdk_url"]
        self.api_key = ONLYOFFICE_CONFIG["api_key"]
        self.jwt_secret = ONLYOFFICE_CONFIG["jwt_secret"]
        self.mode = ONLYOFFICE_CONFIG["mode"]
        self.frame_id = ONLYOFFICE_CONFIG["frame_id"]
    
    def create_onlyoffice_docspace_html(self, width="100%", height="600px") -> str:
        """OnlyOffice DocSpace 편집기 HTML 생성"""
        return f"""
        <div id="{self.frame_id}" style="width: {width}; height: {height};">
            <div style="text-align: center; padding: 20px; color: #6b7280;">
                <h3>📝 OnlyOffice DocSpace 편집기</h3>
                <p>문서 편집기가 로드되고 있습니다...</p>
                <div class="spinner" style="margin: 20px auto; width: 40px; height: 40px; border: 3px solid #f3f3f3; border-top: 3px solid #8b5cf6; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            </div>
        </div>
        
        <script>
        const config = {{
            "src": "{self.docspace_url}",
            "mode": "{self.mode}",
            "width": "{width}",
            "height": "{height}",
            "frameId": "{self.frame_id}",
            "init": false,
            "events": {{
                "onAppReady": function() {{
                    console.log("OnlyOffice DocSpace is ready");
                }},
                "onDocumentReady": function() {{
                    console.log("Document is ready for editing");
                }},
                "onError": function(event) {{
                    console.error("OnlyOffice error:", event);
                }}
            }}
        }};
        
        // SDK 스크립트 로드
        const script = document.createElement("script");
        script.setAttribute("src", "{self.sdk_url}");
        script.onload = () => {{
            if (window.DocSpace && window.DocSpace.SDK) {{
                window.DocSpace.SDK.init(config);
            }} else {{
                console.error("DocSpace SDK not loaded properly");
            }}
        }};
        script.onerror = () => {{
            console.error("Failed to load DocSpace SDK");
        }};
        document.head.appendChild(script);
        </script>
        
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        #{self.frame_id} {{
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background-color: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        </style>
        """
    
    def create_docspace_config(self, file_id: str = None, folder_id: str = None) -> Dict[str, Any]:
        """OnlyOffice DocSpace 설정 생성"""
        config = {
            "src": self.docspace_url,
            "mode": self.mode,
            "width": "100%",
            "height": "600px",
            "frameId": self.frame_id,
            "init": False,
            "editorConfig": {
                "lang": "ko-KR",
                "mode": "edit",
                "user": {
                    "id": "user_1",
                    "name": "Document User"
                },
                "customization": {
                    "autosave": True,
                    "chat": True,
                    "comments": True,
                    "help": True,
                    "plugins": True,
                    "review": True,
                    "zoom": 100
                }
            },
            "events": {
                "onAppReady": "onAppReady",
                "onDocumentReady": "onDocumentReady", 
                "onError": "onError",
                "onRequestSaveAs": "onRequestSaveAs"
            }
        }
        
        # 특정 파일이나 폴더 지정
        if file_id:
            config["fileId"] = file_id
        if folder_id:
            config["folderId"] = folder_id
            
        return config
    
    def create_new_document(self, doc_type: str = "docx", title: str = "새 문서") -> Dict[str, Any]:
        """새 문서 생성"""
        # 실제 구현에서는 OnlyOffice DocSpace API 호출
        return {
            "success": True,
            "file_id": f"new_{doc_type}_{int(time.time())}",
            "title": title,
            "type": doc_type,
            "created_at": time.time()
        }
    
    def extract_text_from_document(self, file_path: str) -> str:
        """문서에서 텍스트 추출"""
        try:
            if file_path.endswith('.docx'):
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text.strip()
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                return "지원되지 않는 파일 형식입니다."
        except Exception as e:
            st.error(f"문서 텍스트 추출 중 오류: {str(e)}")
            return ""
    
    def save_document_content(self, content: str, file_path: str) -> bool:
        """문서 내용 저장"""
        try:
            if file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                return True
            elif file_path.endswith('.docx'):
                from docx import Document
                doc = Document()
                for paragraph in content.split('\n'):
                    doc.add_paragraph(paragraph)
                doc.save(file_path)
                return True
            else:
                st.warning("저장할 수 없는 파일 형식입니다.")
                return False
        except Exception as e:
            st.error(f"문서 저장 중 오류: {str(e)}")
            return False
    
    def handle_onlyoffice_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """OnlyOffice 콜백 처리"""
        try:
            status = callback_data.get('status')
            
            if status == 1:  # 문서가 편집 중
                return {"error": 0}
            elif status == 2:  # 문서가 저장 준비 완료
                download_url = callback_data.get('url')
                if download_url:
                    # 문서 다운로드 및 저장 로직
                    response = requests.get(download_url)
                    if response.status_code == 200:
                        # 파일 저장 로직 구현
                        return {"error": 0}
            elif status == 3:  # 저장 오류
                return {"error": 1}
            elif status == 4:  # 문서가 닫힘
                return {"error": 0}
            elif status == 6:  # 편집 중, 저장 중
                return {"error": 0}
            elif status == 7:  # 강제 저장으로 오류
                return {"error": 1}
            
            return {"error": 0}
            
        except Exception as e:
            st.error(f"OnlyOffice 콜백 처리 중 오류: {str(e)}")
            return {"error": 1}
    
    def search_documents_in_database(self, query: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """데이터베이스에서 문서 검색 (더미 구현)"""
        # 실제 구현에서는 데이터베이스 연동
        dummy_documents = [
            {
                "id": 1,
                "title": "비즈니스 계획서 템플릿",
                "summary": "효과적인 비즈니스 계획서 작성을 위한 체계적인 가이드",
                "content": "비즈니스 계획서는 사업의 방향성과 전략을 명확히 제시하는 중요한 문서입니다...",
                "source": "Business Templates DB",
                "file_type": "docx",
                "created_at": "2024-01-15",
                "relevance_score": 0.9,
                "keywords": ["비즈니스", "계획서", "전략", "사업계획"]
            },
            {
                "id": 2,
                "title": "프로젝트 관리 방법론",
                "summary": "성공적인 프로젝트 수행을 위한 체계적 관리 방법론",
                "content": "프로젝트 관리는 정해진 시간과 예산 내에서 목표를 달성하기 위한 체계적 접근법입니다...",
                "source": "PM Knowledge Base",
                "file_type": "pptx",
                "created_at": "2024-02-20",
                "relevance_score": 0.85,
                "keywords": ["프로젝트", "관리", "방법론", "계획"]
            },
            {
                "id": 3,
                "title": "효과적인 문서 작성 가이드",
                "summary": "명확하고 설득력 있는 문서 작성을 위한 실용적 방법",
                "content": "좋은 문서는 명확한 구조와 논리적 흐름을 바탕으로 작성됩니다...",
                "source": "Writing Excellence Hub",
                "file_type": "docx",
                "created_at": "2024-03-10",
                "relevance_score": 0.8,
                "keywords": ["문서작성", "글쓰기", "커뮤니케이션", "구조화"]
            }
        ]
        
        # 키워드 기반 필터링
        if keywords:
            filtered_docs = []
            for doc in dummy_documents:
                # 키워드 매칭 점수 계산
                matches = 0
                for keyword in keywords:
                    if any(keyword.lower() in doc_keyword.lower() for doc_keyword in doc["keywords"]):
                        matches += 1
                    if keyword.lower() in doc["title"].lower():
                        matches += 1
                    if keyword.lower() in doc["summary"].lower():
                        matches += 1
                
                if matches > 0:
                    doc["relevance_score"] = min(1.0, doc["relevance_score"] + (matches * 0.1))
                    filtered_docs.append(doc)
            
            return sorted(filtered_docs, key=lambda x: x["relevance_score"], reverse=True)
        
        return dummy_documents
    
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        return filename.split('.')[-1].lower()
    
    def _get_document_type(self, filename: str) -> str:
        """문서 타입 결정"""
        ext = self._get_file_extension(filename)
        
        if ext in ['doc', 'docx', 'odt', 'rtf', 'txt']:
            return 'text'
        elif ext in ['xls', 'xlsx', 'ods', 'csv']:
            return 'spreadsheet'
        elif ext in ['ppt', 'pptx', 'odp']:
            return 'presentation'
        else:
            return 'text'
    
    def _generate_document_key(self, filename: str) -> str:
        """문서 키 생성"""
        key_string = f"{filename}_{int(time.time())}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_jwt_token(self, filename: str) -> str:
        """JWT 토큰 생성 (더미)"""
        # 실제 구현에서는 JWT 라이브러리 사용
        return f"jwt_token_for_{filename}"