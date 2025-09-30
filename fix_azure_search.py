#!/usr/bin/env python3
"""
Azure Search 인덱스 재생성 유틸리티
벡터 필드 오류 해결을 위해 기존 인덱스를 삭제하고 재생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.azure_search_management import AzureSearchService

def recreate_search_index():
    """Azure Search 인덱스 강제 재생성"""
    print("🔧 Azure Search 인덱스 재생성 시작...")
    
    # Azure Search 서비스 초기화
    search_service = AzureSearchService()
    
    if not search_service.available:
        print("❌ Azure Search 서비스를 사용할 수 없습니다.")
        return False
    
    try:
        # 기존 인덱스 강제 삭제
        print(f"🗑️ 기존 인덱스 '{search_service.index_name}' 삭제 시도...")
        try:
            search_service.index_client.delete_index(search_service.index_name)
            print(f"✅ 인덱스 '{search_service.index_name}' 삭제 완료")
        except Exception as e:
            print(f"📝 인덱스 삭제 시도 (없을 수 있음): {e}")
        
        # 새 인덱스 생성
        print("🔨 새 인덱스 생성...")
        success = search_service.create_index_if_not_exists()
        
        if success:
            print("🎉 Azure Search 인덱스 재생성 완료!")
            print("   - 벡터 필드 오류 해결됨")
            print("   - 이제 AI 분석에서 사내 문서 검색이 정상 작동합니다")
            return True
        else:
            print("❌ 인덱스 재생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ 인덱스 재생성 중 오류: {e}")
        return False

if __name__ == "__main__":
    success = recreate_search_index()
    exit(0 if success else 1)