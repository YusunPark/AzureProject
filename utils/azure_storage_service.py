"""
Azure Storage Account 서비스
파일 업로드, 다운로드, 관리 기능 제공
"""
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import uuid
from config import AZURE_STORAGE_CONFIG

class AzureStorageService:
    def __init__(self):
        self.available = False
        self.blob_service_client = None
        self.container_name = None
        self._init_storage()
    
    def _init_storage(self):
        """Azure Storage 초기화"""
        try:
            if (AZURE_STORAGE_CONFIG["account_name"] and 
                AZURE_STORAGE_CONFIG["account_key"] and
                AZURE_STORAGE_CONFIG["container_name"]):
                
                connection_string = (
                    f"DefaultEndpointsProtocol=https;"
                    f"AccountName={AZURE_STORAGE_CONFIG['account_name']};"
                    f"AccountKey={AZURE_STORAGE_CONFIG['account_key']};"
                    f"EndpointSuffix=core.windows.net"
                )
                
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                self.container_name = AZURE_STORAGE_CONFIG["container_name"]
                
                # 컨테이너 존재 확인 및 생성
                self._ensure_container_exists()
                self.available = True
                print("✅ Azure Storage 초기화 성공")
                
            else:
                print("⚠️ Azure Storage 설정이 불완전합니다.")
                
        except Exception as e:
            print(f"⚠️ Azure Storage 초기화 실패: {e}")
            self.available = False
    
    def _ensure_container_exists(self):
        """컨테이너 존재 확인 및 생성"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                print(f"✅ 컨테이너 '{self.container_name}' 생성됨")
        except Exception as e:
            print(f"⚠️ 컨테이너 확인/생성 실패: {e}")
    
    def upload_document(self, file_content: bytes, filename: str, 
                       document_type: str = "training", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        문서 업로드
        
        Args:
            file_content: 파일 내용 (bytes)
            filename: 원본 파일명
            document_type: 문서 타입 ('training' 또는 'generated')
            metadata: 추가 메타데이터
            
        Returns:
            업로드 결과 정보
        """
        if not self.available:
            return {
                "success": False,
                "error": "Azure Storage가 사용할 수 없습니다.",
                "filename": filename
            }
        
        try:
            # 고유한 파일 ID 생성
            file_id = str(uuid.uuid4())
            
            # 파일 확장자 추출
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Blob 이름 생성 (폴더 구조: type/year/month/file_id.ext)
            now = datetime.now(timezone.utc)
            blob_name = f"{document_type}/{now.year}/{now.month:02d}/{file_id}{file_ext}"
            
            # 파일명을 안전한 형태로 인코딩 (메타데이터용)
            safe_filename = filename.encode('ascii', errors='ignore').decode('ascii')
            if not safe_filename:
                safe_filename = f"document_{file_id}"
            
            # 메타데이터 설정 (모든 값을 문자열로 변환하고 안전하게 인코딩)
            blob_metadata = {}
            try:
                # 파일명을 여러 방식으로 저장하여 안전성 확보
                import base64
                
                # 1. 원본 파일명 Base64 인코딩
                try:
                    encoded_filename = base64.b64encode(filename.encode('utf-8')).decode('ascii')
                    blob_metadata["original_filename"] = encoded_filename
                except:
                    pass
                
                # 2. ASCII 안전 버전 (영어, 숫자만)
                blob_metadata["safe_filename"] = safe_filename
                
                # 3. 원본 파일명 (한글 포함) - URL 인코딩 방식 시도
                try:
                    import urllib.parse
                    url_encoded_filename = urllib.parse.quote(filename, safe='')
                    blob_metadata["display_name"] = url_encoded_filename
                except:
                    # URL 인코딩 실패 시 원본 그대로 시도
                    try:
                        # Azure 메타데이터는 ASCII만 지원하므로 한글이 포함된 경우 실패할 수 있음
                        blob_metadata["display_name"] = filename
                    except:
                        pass  # 실패해도 계속 진행
                blob_metadata["document_type"] = str(document_type)
                blob_metadata["upload_date"] = now.isoformat()
                blob_metadata["file_id"] = str(file_id)
                blob_metadata["file_size"] = str(len(file_content))
                
                if metadata:
                    for key, value in metadata.items():
                        # 키와 값을 안전하게 인코딩
                        safe_key = str(key).encode('ascii', errors='ignore').decode('ascii')
                        safe_value = str(value).encode('ascii', errors='ignore').decode('ascii')
                        if safe_key and safe_value:
                            blob_metadata[f"meta_{safe_key}"] = safe_value
                            
            except Exception as meta_error:
                print(f"메타데이터 설정 경고: {meta_error}")
                # 기본 메타데이터만 설정
                blob_metadata = {
                    "file_id": str(file_id),
                    "document_type": str(document_type),
                    "upload_date": now.isoformat()
                }
            
            # 파일 업로드
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                metadata=blob_metadata
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "blob_name": blob_name,
                "url": blob_client.url,
                "filename": filename,
                "document_type": document_type,
                "upload_date": now.isoformat(),
                "file_size": len(file_content)
            }
            
        except Exception as e:
            print(f"파일 업로드 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def _decode_filename(self, encoded_filename: str) -> str:
        """Base64로 인코딩된 파일명을 디코딩"""
        try:
            import base64
            # Base64 디코딩 시도
            decoded_bytes = base64.b64decode(encoded_filename.encode('ascii'))
            decoded_filename = decoded_bytes.decode('utf-8')
            return decoded_filename
        except:
            return encoded_filename  # 디코딩 실패 시 원본 반환
    
    def list_documents(self, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        문서 목록 조회
        
        Args:
            document_type: 문서 타입 필터 ('training', 'generated' 또는 None)
            
        Returns:
            문서 목록
        """
        if not self.available:
            return []
        
        try:
            documents = []
            
            # 컨테이너의 모든 블롭 조회
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # 필터 조건 설정
            name_starts_with = f"{document_type}/" if document_type else None
            
            for blob in container_client.list_blobs(name_starts_with=name_starts_with, include=['metadata']):
                # 파일명 디코딩 시도
                original_filename = blob.metadata.get("original_filename", "")
                safe_filename = blob.metadata.get("safe_filename", "")
                
                # 파일명 디코딩 우선 순위:
                # 1. display_name (원본 그대로)
                # 2. Base64 디코딩된 original_filename  
                # 3. safe_filename
                # 4. blob.name에서 추출
                
                decoded_filename = blob.name  # 기본값
                
                # 1단계: display_name 확인 (URL 인코딩되었을 수 있음)
                display_name = blob.metadata.get("display_name", "")
                if display_name:
                    try:
                        # URL 디코딩 시도
                        import urllib.parse
                        decoded_filename = urllib.parse.unquote(display_name)
                    except:
                        # URL 디코딩 실패 시 그대로 사용
                        decoded_filename = display_name
                
                # 2단계: original_filename Base64 디코딩
                elif original_filename:
                    try:
                        import base64
                        import re
                        # Base64 패턴 확인 (영문자, 숫자, +, /, = 로만 구성되고 길이가 4의 배수)
                        if (re.match(r'^[A-Za-z0-9+/]*={0,2}$', original_filename) and 
                            len(original_filename) % 4 == 0 and 
                            len(original_filename) > 10):  # 너무 짧으면 Base64가 아님
                            
                            decoded_filename = self._decode_filename(original_filename)
                        else:
                            # Base64가 아닌 경우 그대로 사용
                            decoded_filename = original_filename
                    except:
                        # 디코딩 실패 시 safe_filename 사용
                        decoded_filename = safe_filename or blob.name
                
                # 3단계: safe_filename 사용
                elif safe_filename:
                    decoded_filename = safe_filename
                
                # 4단계: blob.name에서 파일명 추출
                else:
                    blob_parts = blob.name.split('/')
                    if blob_parts:
                        file_part = blob_parts[-1]  # 마지막 부분이 파일명
                        # UUID 패턴 제거하고 확장자만 남기기
                        if '.' in file_part:
                            ext = file_part.split('.')[-1]
                            decoded_filename = f"문서.{ext}"
                        else:
                            decoded_filename = file_part
                
                doc_info = {
                    "file_id": blob.metadata.get("file_id", "unknown"),
                    "filename": decoded_filename,
                    "blob_name": blob.name,
                    "document_type": blob.metadata.get("document_type", "unknown"),
                    "upload_date": blob.metadata.get("upload_date", "unknown"),
                    "file_size": int(blob.metadata.get("file_size", blob.size or 0)),
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                    "url": f"{self.blob_service_client.url}/{self.container_name}/{blob.name}"
                }
                documents.append(doc_info)
            
            # 업로드 날짜 순으로 정렬
            documents.sort(key=lambda x: x["upload_date"], reverse=True)
            return documents
            
        except Exception as e:
            print(f"문서 목록 조회 실패: {e}")
            return []
    
    def download_document(self, blob_name: str) -> Optional[bytes]:
        """
        문서 다운로드
        
        Args:
            blob_name: 블롭 이름
            
        Returns:
            파일 내용 (bytes) 또는 None
        """
        if not self.available:
            return None
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            return blob_client.download_blob().readall()
            
        except Exception as e:
            print(f"문서 다운로드 실패: {e}")
            return None
    
    def delete_document(self, blob_name: str) -> bool:
        """
        문서 삭제
        
        Args:
            blob_name: 블롭 이름
            
        Returns:
            삭제 성공 여부
        """
        if not self.available:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
            
        except Exception as e:
            print(f"문서 삭제 실패: {e}")
            return False
    
    def get_document_info(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """
        문서 정보 조회
        
        Args:
            blob_name: 블롭 이름
            
        Returns:
            문서 정보 또는 None
        """
        if not self.available:
            return None
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            properties = blob_client.get_blob_properties()
            
            return {
                "blob_name": blob_name,
                "filename": properties.metadata.get("original_filename", blob_name),
                "file_id": properties.metadata.get("file_id", "unknown"),
                "document_type": properties.metadata.get("document_type", "unknown"),
                "upload_date": properties.metadata.get("upload_date", "unknown"),
                "file_size": properties.size,
                "last_modified": properties.last_modified.isoformat() if properties.last_modified else None,
                "content_type": properties.content_settings.content_type,
                "url": blob_client.url,
                "metadata": properties.metadata
            }
            
        except Exception as e:
            print(f"문서 정보 조회 실패: {e}")
            return None
    
    def update_document_metadata(self, blob_name: str, metadata: Dict[str, str]) -> bool:
        """
        문서 메타데이터 업데이트
        
        Args:
            blob_name: 블롭 이름
            metadata: 업데이트할 메타데이터
            
        Returns:
            업데이트 성공 여부
        """
        if not self.available:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # 기존 메타데이터 가져오기
            properties = blob_client.get_blob_properties()
            current_metadata = properties.metadata or {}
            
            # 메타데이터 업데이트
            current_metadata.update(metadata)
            
            # 메타데이터 설정
            blob_client.set_blob_metadata(current_metadata)
            return True
            
        except Exception as e:
            print(f"메타데이터 업데이트 실패: {e}")
            return False
    
    def search_documents(self, query: str, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        문서 검색 (파일명 및 메타데이터 기반)
        
        Args:
            query: 검색 쿼리
            document_type: 문서 타입 필터
            
        Returns:
            검색된 문서 목록
        """
        documents = self.list_documents(document_type)
        
        if not query.strip():
            return documents
        
        # 간단한 텍스트 매칭 검색
        query_lower = query.lower()
        filtered_docs = []
        
        for doc in documents:
            # 파일명에서 검색
            if query_lower in doc["filename"].lower():
                doc["match_reason"] = "파일명 일치"
                filtered_docs.append(doc)
                continue
            
            # 메타데이터에서 검색 (있다면)
            if "metadata" in doc:
                metadata_text = json.dumps(doc["metadata"], ensure_ascii=False).lower()
                if query_lower in metadata_text:
                    doc["match_reason"] = "메타데이터 일치"
                    filtered_docs.append(doc)
        
        return filtered_docs
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """
        스토리지 사용량 통계
        
        Returns:
            스토리지 통계 정보
        """
        if not self.available:
            return {"available": False}
        
        try:
            all_docs = self.list_documents()
            
            stats = {
                "available": True,
                "total_documents": len(all_docs),
                "training_documents": len([d for d in all_docs if d["document_type"] == "training"]),
                "generated_documents": len([d for d in all_docs if d["document_type"] == "generated"]),
                "total_size": sum(d["file_size"] for d in all_docs),
                "container_name": self.container_name,
                "account_name": AZURE_STORAGE_CONFIG["account_name"]
            }
            
            # 월별 업로드 통계 (최근 6개월)
            monthly_stats = {}
            for doc in all_docs:
                try:
                    upload_date = datetime.fromisoformat(doc["upload_date"].replace('Z', '+00:00'))
                    month_key = f"{upload_date.year}-{upload_date.month:02d}"
                    
                    if month_key not in monthly_stats:
                        monthly_stats[month_key] = {"count": 0, "size": 0}
                    
                    monthly_stats[month_key]["count"] += 1
                    monthly_stats[month_key]["size"] += doc["file_size"]
                except:
                    pass
            
            stats["monthly_stats"] = monthly_stats
            return stats
            
        except Exception as e:
            return {
                "available": True,
                "error": str(e),
                "total_documents": 0
            }