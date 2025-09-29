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
        """OnlyOffice DocSpace 편집기 HTML 생성 - CSP 오류 해결 버전"""
        return f"""
        <div id="{self.frame_id}" style="width: {width}; height: {height}; border: 1px solid #e5e7eb; border-radius: 8px; background-color: #ffffff; overflow: hidden;">
            <div id="loading-container" style="text-align: center; padding: 50px; color: #6b7280;">
                <h3>📝 OnlyOffice DocSpace 편집기</h3>
                <p>문서 편집기를 초기화하고 있습니다...</p>
                <div class="loading-spinner"></div>
                <div id="csp-error-info" style="display: none; margin-top: 20px; padding: 15px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
                    <h4 style="color: #dc2626; margin: 0 0 10px 0;">⚠️ CSP 오류 발생</h4>
                    <p style="font-size: 14px; margin: 5px 0;">OnlyOffice DocSpace 도메인 허용 설정을 확인해주세요:</p>
                    <ol style="font-size: 13px; margin: 10px 0; padding-left: 20px;">
                        <li>OnlyOffice DocSpace 관리자 콘솔 접속</li>
                        <li>Developer Tools → JavaScript SDK 메뉴</li>
                        <li>허용 도메인에 다음 URL 추가:</li>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            <li><code>https://appsvc-yusun-01.azurewebsites.net</code></li>
                            <li><code>*.azurewebsites.net</code></li>
                        </ul>
                        <li>설정 저장 후 페이지 새로고침</li>
                    </ol>
                </div>
                <button id="retry-btn" onclick="retryDocSpaceInit()" style="margin-top: 20px; padding: 8px 16px; background: #8b5cf6; color: white; border: none; border-radius: 4px; cursor: pointer; display: none;">다시 시도</button>
                <button onclick="openInNewTab()" style="margin-top: 20px; padding: 8px 16px; background: #059669; color: white; border: none; border-radius: 4px; cursor: pointer; margin-left: 10px;">새 창에서 열기</button>
            </div>
        </div>
        
        <script>
        // CSP 오류 방지를 위한 안전한 초기화
        (function() {{
            let initAttempts = 0;
            const maxAttempts = 3;
            
            function initDocSpace() {{
                initAttempts++;
                
                const config = {{
                    "src": "{self.docspace_url}",
                    "mode": "{self.mode}",
                    "width": "{width}",
                    "height": "{height}",
                    "frameId": "{self.frame_id}",
                    "init": false,
                    "type": "desktop",
                    "editorConfig": {{
                        "lang": "ko-KR",
                        "mode": "edit",
                        "user": {{
                            "id": "streamlit_user_" + Date.now(),
                            "name": "Streamlit User"
                        }},
                        "customization": {{
                            "autosave": true,
                            "chat": false,
                            "comments": true,
                            "help": true,
                            "plugins": false,
                            "review": true,
                            "zoom": 100,
                            "compactToolbar": true
                        }}
                    }},
                    "events": {{
                        "onAppReady": function() {{
                            console.log("DocSpace App Ready");
                            document.getElementById("loading-container").style.display = "none";
                        }},
                        "onDocumentReady": function() {{
                            console.log("Document Ready");
                        }},
                        "onError": function(event) {{
                            console.error("DocSpace Error:", event);
                            handleDocSpaceError();
                        }}
                    }}
                }};
                
                // SDK 스크립트가 이미 로드되어 있는지 확인
                if (window.DocSpace && window.DocSpace.SDK) {{
                    try {{
                        window.DocSpace.SDK.init(config);
                    }} catch (error) {{
                        console.error("DocSpace init error:", error);
                        handleDocSpaceError();
                    }}
                }} else {{
                    // SDK 동적 로드
                    loadDocSpaceSDK(config);
                }}
            }}
            
            function loadDocSpaceSDK(config) {{
                const script = document.createElement("script");
                script.src = "{self.sdk_url}";
                script.async = true;
                script.defer = true;
                
                script.onload = function() {{
                    console.log("DocSpace SDK loaded successfully");
                    setTimeout(() => {{
                        if (window.DocSpace && window.DocSpace.SDK) {{
                            try {{
                                window.DocSpace.SDK.init(config);
                            }} catch (error) {{
                                console.error("DocSpace SDK init error:", error);
                                handleDocSpaceError();
                            }}
                        }} else {{
                            console.error("DocSpace SDK not available after load");
                            handleDocSpaceError();
                        }}
                    }}, 500);
                }};
                
                script.onerror = function(error) {{
                    console.error("Failed to load DocSpace SDK:", error);
                    handleDocSpaceError();
                }};
                
                // CSP 오류 방지를 위해 head가 아닌 body에 추가
                if (document.body) {{
                    document.body.appendChild(script);
                }} else {{
                    document.addEventListener("DOMContentLoaded", function() {{
                        document.body.appendChild(script);
                    }});
                }}
            }}
            
            function handleDocSpaceError() {{
                const container = document.getElementById("loading-container");
                const cspErrorInfo = document.getElementById("csp-error-info");
                const retryBtn = document.getElementById("retry-btn");
                
                if (container && cspErrorInfo) {{
                    cspErrorInfo.style.display = "block";
                    retryBtn.style.display = "inline-block";
                }}
            }}
            
            // 새 창에서 열기 함수 추가
            window.openInNewTab = function() {{
                window.open('{self.docspace_url}', '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes,toolbar=yes');
            }};
            
            // 전역 함수로 등록
            window.retryDocSpaceInit = function() {{
                if (initAttempts < maxAttempts) {{
                    document.getElementById("loading-container").innerHTML = `
                        <div style="text-align: center; padding: 20px;">
                            <p>다시 시도하는 중... (${{initAttempts + 1}}/${{maxAttempts}})</p>
                            <div class="loading-spinner"></div>
                        </div>
                    `;
                    setTimeout(initDocSpace, 1000);
                }} else {{
                    alert("최대 시도 횟수를 초과했습니다. 페이지를 새로고침해주세요.");
                }}
            }};
            
            // 페이지 로드 완료 후 초기화
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initDocSpace);
            }} else {{
                setTimeout(initDocSpace, 100);
            }}
        }})();
        </script>
        
        <style>
        .loading-spinner {{
            width: 40px;
            height: 40px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #8b5cf6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        #{self.frame_id} {{
            position: relative;
        }}
        
        #{self.frame_id} iframe {{
            width: 100% !important;
            height: 100% !important;
            border: none;
        }}
        
        code {{
            background-color: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            color: #1e40af;
        }}
        </style>
        """
    
    def create_alternative_docspace_iframe(self, width="100%", height="600px") -> str:
        """대안: iframe을 통한 OnlyOffice DocSpace 통합 - 개선 버전"""
        return f"""
        <div style="width: {width}; height: {height}; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; position: relative;">
            <div id="iframe-container" style="width: 100%; height: 100%; position: relative;">
                <iframe id="onlyoffice-iframe"
                    src="{self.docspace_url}/rooms/shared"
                    width="100%" 
                    height="100%" 
                    frameborder="0"
                    allow="clipboard-read; clipboard-write; microphone; camera; display-capture"
                    sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-downloads allow-top-navigation"
                    referrerpolicy="no-referrer-when-downgrade"
                    style="border: none;">
                </iframe>
                
                <div id="iframe-overlay" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.9); display: none; z-index: 10;">
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                        <h4>문서 편집기 로딩 중...</h4>
                        <p>잠시만 기다려주세요.</p>
                    </div>
                </div>
            </div>
            
            <div style="position: absolute; bottom: 10px; right: 10px; z-index: 5;">
                <button onclick="refreshIframe()" style="padding: 8px 12px; background: #8b5cf6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    🔄 새로고침
                </button>
                <button onclick="openInNewWindow()" style="padding: 8px 12px; background: #059669; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 5px;">
                    🚀 새 창에서 열기
                </button>
            </div>
        </div>
        
        <script>
        function refreshIframe() {{
            const iframe = document.getElementById('onlyoffice-iframe');
            const overlay = document.getElementById('iframe-overlay');
            
            overlay.style.display = 'block';
            iframe.src = iframe.src;
            
            setTimeout(() => {{
                overlay.style.display = 'none';
            }}, 3000);
        }}
        
        function openInNewWindow() {{
            window.open('{self.docspace_url}', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
        }}
        
        // iframe 로드 감지
        document.getElementById('onlyoffice-iframe').onload = function() {{
            console.log('OnlyOffice iframe loaded');
        }};
        </script>
        
        <style>
        #onlyoffice-iframe {{
            border: none !important;
        }}
        
        button:hover {{
            opacity: 0.8;
        }}
        </style>
        """
    
    def create_direct_editor_iframe(self, file_id: str = None, width="100%", height="600px") -> str:
        """직접 문서 편집기 iframe 생성"""
        # 특정 파일 ID가 있으면 직접 편집기로 연결
        if file_id:
            editor_url = f"{self.docspace_url}/doceditor?fileId={file_id}"
        else:
            # 새 문서 생성 또는 기본 편집기
            editor_url = f"{self.docspace_url}/products/files/"
        
        return f"""
        <div style="width: {width}; height: {height}; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; position: relative;">
            <div style="background: #f8f9fa; padding: 10px; border-bottom: 1px solid #e5e7eb; font-size: 14px;">
                <span style="color: #6b7280;">📝 OnlyOffice 문서 편집기</span>
                <span style="float: right;">
                    <button onclick="refreshEditor()" style="padding: 4px 8px; background: #8b5cf6; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 11px; margin-right: 5px;">새로고침</button>
                    <button onclick="openFullEditor()" style="padding: 4px 8px; background: #059669; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 11px;">전체화면</button>
                </span>
            </div>
            
            <iframe id="direct-editor-iframe"
                src="{editor_url}"
                width="100%" 
                height="100%" 
                frameborder="0"
                allow="clipboard-read; clipboard-write; microphone; camera; display-capture; fullscreen"
                sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-downloads allow-top-navigation-by-user-activation"
                referrerpolicy="no-referrer-when-downgrade"
                style="border: none;">
                <p>OnlyOffice 편집기를 로드할 수 없습니다.</p>
                <p><a href="{editor_url}" target="_blank">새 창에서 열기</a></p>
            </iframe>
        </div>
        
        <script>
        function refreshEditor() {{
            const iframe = document.getElementById('direct-editor-iframe');
            iframe.src = iframe.src;
        }}
        
        function openFullEditor() {{
            window.open('{editor_url}', '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes,toolbar=no,menubar=no');
        }}
        </script>
        """
    
    def create_embedded_editor_option(self, width="100%", height="600px") -> str:
        """임베디드 에디터 통합 옵션"""
        return f"""
        <div style="width: {width}; height: {height}; border: 1px solid #e5e7eb; border-radius: 8px; background-color: #f9fafb; display: flex; flex-direction: column;">
            
            <div style="padding: 20px; border-bottom: 1px solid #e5e7eb; background: white;">
                <h4 style="margin: 0 0 15px 0; color: #1f2937;">📝 OnlyOffice 문서 편집 옵션</h4>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    
                    <div style="padding: 15px; border: 1px solid #e5e7eb; border-radius: 6px; background: white;">
                        <h5 style="margin: 0 0 10px 0; color: #374151;">📄 새 텍스트 문서</h5>
                        <button onclick="createNewDocument('docx')" 
                                style="width: 100%; padding: 8px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Word 문서 생성
                        </button>
                    </div>
                    
                    <div style="padding: 15px; border: 1px solid #e5e7eb; border-radius: 6px; background: white;">
                        <h5 style="margin: 0 0 10px 0; color: #374151;">📊 새 프레젠테이션</h5>
                        <button onclick="createNewDocument('pptx')" 
                                style="width: 100%; padding: 8px; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            PowerPoint 생성
                        </button>
                    </div>
                    
                    <div style="padding: 15px; border: 1px solid #e5e7eb; border-radius: 6px; background: white;">
                        <h5 style="margin: 0 0 10px 0; color: #374151;">📈 새 스프레드시트</h5>
                        <button onclick="createNewDocument('xlsx')" 
                                style="width: 100%; padding: 8px; background: #059669; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Excel 문서 생성
                        </button>
                    </div>
                    
                </div>
            </div>
            
            <div style="flex: 1; padding: 20px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <div style="text-align: center; color: #6b7280;">
                    <h3 style="color: #374151;">🚀 OnlyOffice DocSpace</h3>
                    <p style="margin: 15px 0;">완전한 기능을 사용하려면 별도 창에서 열어주세요.</p>
                    
                    <div style="margin: 20px 0;">
                        <button onclick="openDocSpace()" 
                                style="padding: 12px 24px; background: #8b5cf6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 5px;">
                            📝 DocSpace 열기
                        </button>
                        <button onclick="openWithFileId()" 
                                style="padding: 12px 24px; background: #059669; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 5px;">
                            📁 기존 문서 열기
                        </button>
                    </div>
                    
                    <div style="font-size: 14px; color: #9ca3af; margin-top: 20px;">
                        <p><strong>팁:</strong> iframe 제한을 우회하려면</p>
                        <ul style="text-align: left; display: inline-block;">
                            <li>새 창에서 OnlyOffice를 열어 문서 작성</li>
                            <li>작성된 내용을 복사하여 아래 텍스트 영역에 붙여넣기</li>
                            <li>AI 분석 기능으로 문서 개선</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function createNewDocument(type) {{
            const urls = {{
                'docx': '{self.docspace_url}/products/files/',
                'pptx': '{self.docspace_url}/products/files/', 
                'xlsx': '{self.docspace_url}/products/files/'
            }};
            
            window.open(urls[type], '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');
        }}
        
        function openDocSpace() {{
            window.open('{self.docspace_url}', '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');
        }}
        
        function openWithFileId() {{
            const fileId = prompt('파일 ID를 입력하세요 (예: 2403165):');
            if (fileId) {{
                const url = '{self.docspace_url}/doceditor?fileId=' + fileId;
                window.open(url, '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');
            }}
        }}
        </script>
        
        <style>
        button:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}
        
        button:active {{
            transform: translateY(0);
        }}
        </style>
        """
    
    def create_external_link_option(self) -> str:
        """외부 링크로 OnlyOffice 열기 옵션"""
        return f"""
        <div style="text-align: center; padding: 40px; border: 1px solid #e5e7eb; border-radius: 8px; background-color: #f9fafb;">
            <h3>📝 OnlyOffice DocSpace</h3>
            <p style="color: #6b7280; margin: 20px 0;">
                CSP 정책으로 인해 임베딩이 제한되었습니다.<br>
                새 창에서 OnlyOffice DocSpace를 사용하세요.
            </p>
            
            <div style="margin: 20px 0;">
                <a href="{self.docspace_url}" 
                   target="_blank" 
                   style="display: inline-block; padding: 12px 24px; background-color: #8b5cf6; color: white; text-decoration: none; border-radius: 6px; font-weight: 500;">
                    🚀 OnlyOffice DocSpace 열기
                </a>
            </div>
            
            <div style="font-size: 14px; color: #6b7280; margin-top: 20px;">
                <p><strong>해결 방법:</strong></p>
                <ol style="text-align: left; max-width: 400px; margin: 0 auto;">
                    <li>OnlyOffice DocSpace 관리자 설정</li>
                    <li>Developer Tools → JavaScript SDK</li>
                    <li>허용 도메인에 추가: <code>http://localhost:8502</code></li>
                </ol>
            </div>
        </div>
        """

    # ... 나머지 메서드들은 그대로 유지 ...
    
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