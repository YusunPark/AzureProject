"""
통합 문서 관리 서비스
Azure Storage + Azure AI Search 연동
"""
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import streamlit as st

from utils.azure_storage_service import AzureStorageService
from utils.azure_search_management import AzureSearchService

class DocumentManagementService:
    def __init__(self):
        self.storage_service = AzureStorageService()
        self.search_service = AzureSearchService()
        self.is_available = self.storage_service.available or self.search_service.available
    
    def upload_training_document(self, file_content: bytes, filename: str, 
                                metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        사내 학습 문서 업로드 (Storage + Search)
        
        Args:
            file_content: 파일 내용
            filename: 파일명
            metadata: 추가 메타데이터
            
        Returns:
            업로드 결과
        """
        results = {
            "filename": filename,
            "storage_result": None,
            "search_result": None,
            "success": False,
            "errors": []
        }
        
        try:
            # 1단계: Azure Storage에 업로드
            if self.storage_service.available:
                storage_result = self.storage_service.upload_document(
                    file_content=file_content,
                    filename=filename,
                    document_type="training",
                    metadata=metadata
                )
                results["storage_result"] = storage_result
                
                if storage_result["success"]:
                    file_id = storage_result["file_id"]
                    blob_url = storage_result["url"]
                    
                    # 2단계: Azure AI Search에 인덱싱
                    if self.search_service.available:
                        search_result = self.search_service.upload_document_to_search(
                            file_content=file_content,
                            filename=filename,
                            file_id=file_id,
                            blob_url=blob_url,
                            metadata=metadata
                        )
                        results["search_result"] = search_result
                        
                        if not search_result["success"]:
                            results["errors"].append(f"검색 인덱싱 실패: {search_result.get('error', 'Unknown')}")
                    else:
                        results["errors"].append("Azure Search 서비스를 사용할 수 없습니다")
                    
                    results["success"] = storage_result["success"]
                else:
                    results["errors"].append(f"스토리지 업로드 실패: {storage_result.get('error', 'Unknown')}")
                    
            else:
                results["errors"].append("Azure Storage 서비스를 사용할 수 없습니다")
            
            return results
            
        except Exception as e:
            results["errors"].append(f"업로드 중 예외 발생: {str(e)}")
            return results
    
    def save_generated_document(self, content: str, title: str, 
                              document_id: Optional[str] = None,
                              metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        생성된 문서 저장
        
        Args:
            content: 문서 내용
            title: 문서 제목
            document_id: 기존 문서 ID (업데이트용)
            metadata: 추가 메타데이터
            
        Returns:
            저장 결과
        """
        results = {
            "title": title,
            "storage_result": None,
            "success": False,
            "errors": []
        }
        
        try:
            if not self.storage_service.available:
                results["errors"].append("Azure Storage 서비스를 사용할 수 없습니다")
                return results
            
            # 제목을 안전한 파일명으로 변환
            import re
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)  # 윈도우 파일명 금지문자 제거
            filename = f"{safe_title}.txt" if not safe_title.endswith('.txt') else safe_title
            
            # UTF-8로 인코딩하여 바이트로 변환
            try:
                file_content = content.encode('utf-8')
            except Exception as encoding_error:
                results["errors"].append(f"문서 내용 인코딩 실패: {str(encoding_error)}")
                return results
            
            # 메타데이터 설정 (ASCII 안전 문자열만 사용)
            save_metadata = {
                "document_id": document_id or str(uuid.uuid4()),
                "created_date": datetime.now().isoformat(),
                "content_length": str(len(content)),
                "word_count": str(len(content.split())),
                "encoding": "utf-8"
            }
            
            # 추가 메타데이터는 안전하게 변환
            if metadata:
                for key, value in metadata.items():
                    # ASCII로 변환 가능한 문자만 저장
                    try:
                        safe_key = str(key).encode('ascii', errors='ignore').decode('ascii')
                        safe_value = str(value).encode('ascii', errors='ignore').decode('ascii')
                        if safe_key and safe_value:
                            save_metadata[safe_key] = safe_value
                    except:
                        continue  # 변환 실패한 메타데이터는 무시
            
            # Azure Storage에 저장
            storage_result = self.storage_service.upload_document(
                file_content=file_content,
                filename=filename,
                document_type="generated",
                metadata=save_metadata
            )
            
            results["storage_result"] = storage_result
            results["success"] = storage_result["success"]
            
            if not storage_result["success"]:
                results["errors"].append(f"저장 실패: {storage_result.get('error', 'Unknown')}")
            
            return results
            
        except Exception as e:
            print(f"문서 저장 중 오류: {str(e)}")
            results["errors"].append(f"저장 중 예외 발생: {str(e)}")
            return results
    
    def search_training_documents(self, query: str, top: int = 10) -> List[Dict[str, Any]]:
        """
        사내 학습 문서 검색
        
        Args:
            query: 검색 쿼리
            top: 반환할 결과 수
            
        Returns:
            검색 결과 목록
        """
        if self.search_service.available:
            return self.search_service.search_documents(
                query=query,
                top=top,
                document_type="training"
            )
        else:
            # 폴백: Storage 메타데이터 기반 검색
            if self.storage_service.available:
                return self.storage_service.search_documents(
                    query=query,
                    document_type="training"
                )
            else:
                return []
    
    def list_training_documents(self) -> List[Dict[str, Any]]:
        """
        모든 사내 학습 문서 목록 조회
        
        Returns:
            문서 목록
        """
        documents = []
        
        # Azure Search에서 조회 시도
        if self.search_service.available:
            search_docs = self.search_service.search_documents(
                query="*",
                top=1000,
                document_type="training",
                use_semantic=False
            )
            
            for doc in search_docs:
                documents.append({
                    "file_id": doc["file_id"],
                    "title": doc["title"],
                    "filename": doc["filename"],
                    "summary": doc.get("summary", ""),
                    "keywords": doc.get("keywords", ""),
                    "upload_date": doc["upload_date"],
                    "file_size": doc.get("file_size", 0),
                    "blob_url": doc.get("blob_url", ""),
                    "source": "search_index"
                })
        
        # Storage에서 조회 시도 (Search가 없거나 추가 정보 필요시)
        if self.storage_service.available:
            storage_docs = self.storage_service.list_documents(document_type="training")
            
            # Search 결과와 중복 제거하면서 병합
            existing_file_ids = {doc["file_id"] for doc in documents}
            
            for doc in storage_docs:
                if doc["file_id"] not in existing_file_ids:
                    documents.append({
                        "file_id": doc["file_id"],
                        "title": doc["filename"].rsplit('.', 1)[0],
                        "filename": doc["filename"],
                        "summary": f"파일 크기: {doc['file_size']} bytes",
                        "keywords": "",
                        "upload_date": doc["upload_date"],
                        "file_size": doc["file_size"],
                        "blob_url": doc["url"],
                        "source": "storage_only"
                    })
        
        # 업로드 날짜 순으로 정렬
        documents.sort(key=lambda x: x["upload_date"], reverse=True)
        return documents
    
    def list_generated_documents(self) -> List[Dict[str, Any]]:
        """
        생성된 문서 목록 조회
        
        Returns:
            문서 목록
        """
        if not self.storage_service.available:
            return []
        
        try:
            storage_docs = self.storage_service.list_documents(document_type="generated")
            
            documents = []
            for doc in storage_docs:
                documents.append({
                    "file_id": doc["file_id"],
                    "title": doc["filename"].rsplit('.', 1)[0],
                    "filename": doc["filename"],
                    "upload_date": doc["upload_date"],
                    "file_size": doc["file_size"],
                    "blob_url": doc["url"],
                    "last_modified": doc.get("last_modified", ""),
                    "document_type": "generated"
                })
            
            # 수정 날짜 순으로 정렬
            documents.sort(key=lambda x: x.get("last_modified", x["upload_date"]), reverse=True)
            return documents
            
        except Exception as e:
            print(f"생성 문서 목록 조회 실패: {e}")
            return []
    
    def get_document_content(self, file_id: str) -> Optional[str]:
        """
        문서 내용 조회
        
        Args:
            file_id: 파일 ID
            
        Returns:
            문서 내용 또는 None
        """
        try:
            # Storage에서 문서 정보 조회
            if self.storage_service.available:
                documents = self.storage_service.list_documents()
                target_doc = None
                
                for doc in documents:
                    if doc["file_id"] == file_id:
                        target_doc = doc
                        break
                
                if target_doc:
                    # 파일 다운로드
                    file_content = self.storage_service.download_document(target_doc["blob_name"])
                    if file_content:
                        return file_content.decode('utf-8', errors='ignore')
            
            return None
            
        except Exception as e:
            print(f"문서 내용 조회 실패: {e}")
            return None
    
    def delete_document(self, file_id: str) -> Dict[str, Any]:
        """
        문서 삭제 (Storage + Search)
        
        Args:
            file_id: 파일 ID
            
        Returns:
            삭제 결과
        """
        results = {
            "file_id": file_id,
            "storage_deleted": False,
            "search_deleted": False,
            "success": False,
            "errors": []
        }
        
        try:
            # Storage에서 삭제할 문서 찾기
            if self.storage_service.available:
                documents = self.storage_service.list_documents()
                target_doc = None
                
                for doc in documents:
                    if doc["file_id"] == file_id:
                        target_doc = doc
                        break
                
                if target_doc:
                    # Storage에서 삭제
                    storage_deleted = self.storage_service.delete_document(target_doc["blob_name"])
                    results["storage_deleted"] = storage_deleted
                    
                    if not storage_deleted:
                        results["errors"].append("Storage에서 삭제 실패")
                else:
                    results["errors"].append("Storage에서 문서를 찾을 수 없음")
            
            # Search에서 삭제
            if self.search_service.available:
                search_doc_id = f"doc_{file_id}"
                search_deleted = self.search_service.delete_document(search_doc_id)
                results["search_deleted"] = search_deleted
                
                if not search_deleted:
                    results["errors"].append("Search 인덱스에서 삭제 실패")
            
            results["success"] = results["storage_deleted"] or results["search_deleted"]
            return results
            
        except Exception as e:
            results["errors"].append(f"삭제 중 예외 발생: {str(e)}")
            return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        문서 관리 통계 정보
        
        Returns:
            통계 정보
        """
        stats = {
            "storage_available": self.storage_service.available,
            "search_available": self.search_service.available,
            "total_training_documents": 0,
            "total_generated_documents": 0,
            "storage_stats": {},
            "search_stats": {}
        }
        
        try:
            # Storage 통계
            if self.storage_service.available:
                storage_stats = self.storage_service.get_storage_statistics()
                stats["storage_stats"] = storage_stats
                stats["total_training_documents"] = storage_stats.get("training_documents", 0)
                stats["total_generated_documents"] = storage_stats.get("generated_documents", 0)
            
            # Search 통계
            if self.search_service.available:
                search_stats = self.search_service.get_search_statistics()
                stats["search_stats"] = search_stats
            
            return stats
            
        except Exception as e:
            stats["error"] = str(e)
            return stats

    def test_services(self) -> Dict[str, Any]:
        """
        서비스 연결 테스트
        
        Returns:
            테스트 결과
        """
        return {
            "storage_service": {
                "available": self.storage_service.available,
                "container_name": getattr(self.storage_service, 'container_name', None),
                "account_name": "Azure Storage" if self.storage_service.available else None
            },
            "search_service": {
                "available": self.search_service.available,
                "index_name": getattr(self.search_service, 'index_name', None),
                "has_embedding": getattr(self.search_service, 'openai_client', None) is not None
            },
            "overall_available": self.is_available
        }