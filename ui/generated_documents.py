"""
생성된 문서 관리 UI
"""
import streamlit as st
import time
from typing import List, Dict, Any
from datetime import datetime

def render_generated_documents_page(doc_manager):
    """생성된 문서 관리 페이지"""
    st.markdown("## 📄 생성된 문서 관리")
    st.markdown("AI로 작성한 문서들을 관리하고 다시 편집할 수 있습니다.")
    
    # 서비스 상태 확인
    if not doc_manager.storage_service.available:
        st.error("🚫 Azure Storage 서비스를 사용할 수 없습니다. 설정을 확인해주세요.")
        return
    
    # 탭으로 구성
    tabs = st.tabs(["📋 문서 목록", "📊 통계", "🔧 관리 도구"])
    
    with tabs[0]:
        render_documents_list(doc_manager)
    
    with tabs[1]:
        render_statistics(doc_manager)
    
    with tabs[2]:
        render_management_tools(doc_manager)

def render_documents_list(doc_manager):
    """생성된 문서 목록"""
    st.markdown("### 📋 생성된 문서 목록")
    
    # 검색 및 필터
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "문서 검색",
            placeholder="제목, 내용으로 검색...",
            key="generated_docs_search"
        )
    
    with col2:
        sort_option = st.selectbox(
            "정렬 기준",
            ["최근 수정순", "제목순", "크기순"],
            key="sort_generated_docs"
        )
    
    with col3:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()
    
    # 문서 목록 가져오기
    with st.spinner("📄 문서 목록을 불러오는 중..."):
        documents = doc_manager.list_generated_documents()
        
        # 검색 필터링
        if search_query and search_query.strip():
            query_lower = search_query.lower().strip()
            documents = [
                doc for doc in documents
                if query_lower in doc['title'].lower() or 
                   query_lower in doc['filename'].lower()
            ]
        
        # 정렬
        if sort_option == "제목순":
            documents.sort(key=lambda x: x['title'].lower())
        elif sort_option == "크기순":
            documents.sort(key=lambda x: x['file_size'], reverse=True)
        # 기본값은 최근 수정순 (이미 정렬됨)
    
        if not documents:
            st.info("📝 생성된 문서가 없습니다. 문서 편집기에서 문서를 작성하고 저장해보세요.")
            
            # 새 문서 생성 버튼
            if st.button("📝 새 문서 작성하기", type="primary", key="create_new_doc_from_manage"):
                st.session_state.main_view = "document_create"
                st.session_state.current_view = "create"
                st.session_state.current_document = None
                st.rerun()
            return    # 문서 통계
    total_docs = len(documents)
    total_size = sum(doc['file_size'] for doc in documents)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 문서 수", total_docs)
    with col2:
        st.metric("총 크기", f"{total_size / 1024:.1f} KB")
    with col3:
        avg_size = total_size / total_docs if total_docs > 0 else 0
        st.metric("평균 크기", f"{avg_size / 1024:.1f} KB")
    
    st.markdown("---")
    
    # 문서 카드 표시
    for doc in documents:
        render_document_card(doc_manager, doc)

def render_document_card(doc_manager, doc):
    """문서 카드 렌더링"""
    with st.expander(f"📄 {doc['title']}", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 문서 정보
            st.markdown(f"**파일명:** {doc['filename']}")
            st.markdown(f"**생성일:** {format_date(doc['upload_date'])}")
            
            if doc.get('last_modified'):
                st.markdown(f"**수정일:** {format_date(doc['last_modified'])}")
            
            st.markdown(f"**크기:** {doc['file_size']:,} bytes ({doc['file_size']/1024:.1f} KB)")
            
            # 내용 미리보기
            preview = get_document_preview(doc_manager, doc['file_id'])
            if preview:
                st.markdown("**내용 미리보기:**")
                st.text_area(
                    f"preview_{doc['file_id']}", 
                    preview, 
                    height=100, 
                    disabled=True, 
                    label_visibility="collapsed"
                )
        
        with col2:
            # 액션 버튼들
            st.markdown("#### 📋 작업")
            
            # 편집 버튼
            if st.button("✏️ 편집", key=f"edit_{doc['file_id']}", use_container_width=True):
                load_document_for_editing(doc_manager, doc)
            
            # 복사 버튼
            if st.button("📋 복사", key=f"copy_{doc['file_id']}", use_container_width=True):
                copy_document(doc_manager, doc)
            
            # 다운로드 버튼
            content = doc_manager.get_document_content(doc['file_id'])
            if content:
                st.download_button(
                    label="💾 다운로드",
                    data=content,
                    file_name=doc['filename'],
                    mime="text/plain",
                    key=f"download_{doc['file_id']}",
                    use_container_width=True
                )
            
            # AI 분석 버튼
            if st.button("🤖 AI 분석", key=f"ai_analyze_{doc['file_id']}", use_container_width=True):
                content = doc_manager.get_document_content(doc['file_id'])
                if content:
                    st.session_state['selected_text'] = content[:1000] if len(content) > 1000 else content
                    st.session_state['ai_panel_open'] = True
                    st.success("이 문서로 AI 분석을 시작합니다.")
            
            # 삭제 버튼
            if st.button("🗑️ 삭제", key=f"delete_gen_{doc['file_id']}", type="secondary", use_container_width=True):
                confirm_key = f'confirm_delete_gen_{doc["file_id"]}'
                if st.session_state.get(confirm_key, False):
                    delete_result = doc_manager.delete_document(doc['file_id'])
                    if delete_result['success']:
                        st.success(f"✅ '{doc['title']}' 삭제 완료")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ 삭제 실패: {', '.join(delete_result['errors'])}")
                else:
                    st.session_state[confirm_key] = True
                    st.warning("⚠️ 다시 한번 클릭하면 삭제됩니다.")

def get_document_preview(doc_manager, file_id: str) -> str:
    """문서 미리보기 생성"""
    content = doc_manager.get_document_content(file_id)
    if content:
        # 처음 200자만 미리보기로 표시
        preview = content[:200]
        if len(content) > 200:
            preview += "..."
        return preview
    return ""

def load_document_for_editing(doc_manager, doc):
    """문서를 편집기로 로드"""
    content = doc_manager.get_document_content(doc['file_id'])
    if content:
        # 세션 상태 업데이트
        st.session_state.current_document = {
            'id': doc['file_id'],
            'type': 'existing',
            'title': doc['title']
        }
        st.session_state.document_content = content
        st.session_state.current_view = "editor"
        
        st.success(f"✅ '{doc['title']}' 문서를 편집기로 로드했습니다.")
        time.sleep(1)
        st.rerun()
    else:
        st.error("문서 내용을 불러올 수 없습니다.")

def copy_document(doc_manager, doc):
    """문서 복사"""
    content = doc_manager.get_document_content(doc['file_id'])
    if content:
        # 새 제목으로 복사
        new_title = f"{doc['title']}_복사본_{int(time.time())}"
        
        result = doc_manager.save_generated_document(
            content=content,
            title=new_title,
            metadata={
                "original_document_id": doc['file_id'],
                "copied_from": doc['title'],
                "copy_date": datetime.now().isoformat()
            }
        )
        
        if result['success']:
            st.success(f"✅ 문서가 '{new_title}'로 복사되었습니다.")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ 복사 실패: {', '.join(result['errors'])}")
    else:
        st.error("원본 문서를 불러올 수 없습니다.")

def render_statistics(doc_manager):
    """통계 정보 표시"""
    st.markdown("### 📊 문서 통계")
    
    with st.spinner("📊 통계 정보를 수집하는 중..."):
        stats = doc_manager.get_statistics()
        documents = doc_manager.list_generated_documents()
    
    if not documents:
        st.info("통계를 표시할 문서가 없습니다.")
        return
    
    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 문서 수", len(documents))
    
    with col2:
        total_size = sum(doc['file_size'] for doc in documents)
        st.metric("총 크기", f"{total_size / (1024*1024):.2f} MB")
    
    with col3:
        avg_size = total_size / len(documents) if documents else 0
        st.metric("평균 크기", f"{avg_size / 1024:.1f} KB")
    
    with col4:
        # 최근 7일간 생성된 문서 수
        recent_count = count_recent_documents(documents, days=7)
        st.metric("최근 7일", f"{recent_count}개")
    
    st.markdown("---")
    
    # 월별 생성 통계
    if stats.get("storage_stats", {}).get("monthly_stats"):
        st.markdown("#### 📈 월별 문서 생성 통계")
        
        monthly_stats = stats["storage_stats"]["monthly_stats"]
        
        # 생성된 문서만 필터링
        generated_monthly = {}
        for doc in documents:
            try:
                upload_date = datetime.fromisoformat(doc["upload_date"].replace('Z', '+00:00'))
                month_key = f"{upload_date.year}-{upload_date.month:02d}"
                
                if month_key not in generated_monthly:
                    generated_monthly[month_key] = {"count": 0, "size": 0}
                
                generated_monthly[month_key]["count"] += 1
                generated_monthly[month_key]["size"] += doc["file_size"]
            except:
                pass
        
        if generated_monthly:
            months = sorted(generated_monthly.keys())[-6:]  # 최근 6개월
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**월별 문서 수**")
                for month in months:
                    count = generated_monthly[month]["count"]
                    st.metric(month, f"{count}개")
            
            with col2:
                st.markdown("**월별 총 크기**")
                for month in months:
                    size_mb = generated_monthly[month]["size"] / (1024*1024)
                    st.metric(month, f"{size_mb:.1f} MB")
    
    # 크기별 분포
    st.markdown("#### 📏 파일 크기 분포")
    
    size_ranges = {
        "~1KB": 0, "1-10KB": 0, "10-100KB": 0, "100KB~1MB": 0, "1MB+": 0
    }
    
    for doc in documents:
        size = doc['file_size']
        if size < 1024:
            size_ranges["~1KB"] += 1
        elif size < 10*1024:
            size_ranges["1-10KB"] += 1
        elif size < 100*1024:
            size_ranges["10-100KB"] += 1
        elif size < 1024*1024:
            size_ranges["100KB~1MB"] += 1
        else:
            size_ranges["1MB+"] += 1
    
    cols = st.columns(len(size_ranges))
    for i, (range_name, count) in enumerate(size_ranges.items()):
        with cols[i]:
            percentage = (count / len(documents)) * 100 if documents else 0
            st.metric(range_name, count, delta=f"{percentage:.1f}%")

def render_management_tools(doc_manager):
    """관리 도구"""
    st.markdown("### 🔧 문서 관리 도구")
    
    # 일괄 작업
    st.markdown("#### 🔄 일괄 작업")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗂️ 모든 문서 백업", use_container_width=True):
            backup_all_documents(doc_manager)
    
    with col2:
        if st.button("🧹 임시 파일 정리", use_container_width=True):
            cleanup_temp_files(doc_manager)
    
    # 서비스 상태
    st.markdown("#### 🔍 서비스 상태")
    
    test_results = doc_manager.test_services()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Azure Storage**")
        if test_results["storage_service"]["available"]:
            st.success("✅ 정상 연결")
            st.info(f"컨테이너: {test_results['storage_service']['container_name']}")
        else:
            st.error("❌ 연결 실패")
    
    with col2:
        st.markdown("**Azure AI Search**")
        if test_results["search_service"]["available"]:
            st.success("✅ 정상 연결")
            st.info(f"인덱스: {test_results['search_service']['index_name']}")
        else:
            st.error("❌ 연결 실패")
    
    # 상세 통계
    if st.button("📊 상세 통계 보기"):
        show_detailed_statistics(doc_manager)

def count_recent_documents(documents: List[Dict], days: int = 7) -> int:
    """최근 N일간 생성된 문서 수 계산"""
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    count = 0
    
    for doc in documents:
        try:
            upload_date = datetime.fromisoformat(doc["upload_date"].replace('Z', '+00:00'))
            if upload_date.replace(tzinfo=None) >= cutoff_date:
                count += 1
        except:
            pass
    
    return count

def backup_all_documents(doc_manager):
    """모든 문서 백업"""
    st.info("🔄 문서 백업 기능은 개발 중입니다.")

def cleanup_temp_files(doc_manager):
    """임시 파일 정리"""
    st.info("🧹 임시 파일 정리 기능은 개발 중입니다.")

def show_detailed_statistics(doc_manager):
    """상세 통계 표시"""
    with st.expander("📊 상세 통계 정보", expanded=True):
        stats = doc_manager.get_statistics()
        st.json(stats)

def format_date(date_string: str) -> str:
    """날짜 형식 변환"""
    try:
        if date_string and date_string != "unknown":
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        else:
            return "날짜 정보 없음"
    except:
        return date_string or "날짜 정보 없음"