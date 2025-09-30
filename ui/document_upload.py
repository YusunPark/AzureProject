"""
사내 문서 업로드 및 관리 UI
"""
import streamlit as st
import time
from typing import List, Dict, Any
from datetime import datetime

def render_document_upload_page(doc_manager):
    """사내 문서 업로드 페이지"""
    st.markdown("## 📚 사내 문서 학습")
    st.markdown("사내 문서를 업로드하여 AI가 학습할 수 있도록 합니다. 업로드된 문서는 Azure AI Search에 인덱싱되어 검색 가능해집니다.")
    
    # 서비스 상태 확인
    if not doc_manager.is_available:
        st.error("🚫 문서 관리 서비스를 사용할 수 없습니다. Azure Storage 또는 Azure AI Search 설정을 확인해주세요.")
        
        # 설정 상태 표시
        with st.expander("🔧 서비스 상태 확인"):
            test_results = doc_manager.test_services()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Azure Storage**")
                if test_results["storage_service"]["available"]:
                    st.success("✅ 연결됨")
                    st.info(f"컨테이너: {test_results['storage_service']['container_name']}")
                else:
                    st.error("❌ 연결 실패")
            
            with col2:
                st.markdown("**Azure AI Search**")
                if test_results["search_service"]["available"]:
                    st.success("✅ 연결됨")
                    st.info(f"인덱스: {test_results['search_service']['index_name']}")
                    if test_results['search_service']['has_embedding']:
                        st.success("🧠 벡터 검색 지원")
                else:
                    st.error("❌ 연결 실패")
        return
    
    # 탭으로 구성
    tabs = st.tabs(["📤 문서 업로드", "📋 업로드된 문서 관리"])
    
    with tabs[0]:
        render_upload_interface(doc_manager)
    
    with tabs[1]:
        render_training_documents_list(doc_manager)

def render_upload_interface(doc_manager):
    """문서 업로드 인터페이스"""
    st.markdown("### 📤 새 문서 업로드")
    
    # 파일 업로드
    uploaded_files = st.file_uploader(
        "학습할 문서를 선택하세요 (여러 파일 선택 가능)",
        type=['txt', 'md', 'docx', 'pdf', 'py', 'js', 'html', 'css', 'json', 'csv'],
        accept_multiple_files=True,
        help="지원 형식: TXT, MD, DOCX, PDF, PY, JS, HTML, CSS, JSON, CSV"
    )
    
    if uploaded_files:
        st.markdown(f"**선택된 파일:** {len(uploaded_files)}개")
        
        # 파일 목록 표시
        for i, file in enumerate(uploaded_files):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"{i+1}. {file.name}")
            with col2:
                file_size = len(file.getvalue())
                st.write(f"{file_size:,} bytes")
            with col3:
                st.write(file.type if file.type else "Unknown")
        
        # 메타데이터 입력
        st.markdown("#### 📝 추가 정보 (선택사항)")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "문서 카테고리",
                ["정책/규정", "가이드라인", "기술문서", "매뉴얼", "보고서", "기타"],
                help="문서의 성격에 맞는 카테고리를 선택하세요"
            )
        
        with col2:
            department = st.text_input(
                "관련 부서",
                placeholder="예: IT팀, HR팀, 마케팅팀",
                help="문서와 관련된 부서명을 입력하세요"
            )
        
        tags = st.text_input(
            "태그 (쉼표로 구분)",
            placeholder="예: 정책, 절차, 가이드",
            help="검색에 도움이 될 키워드들을 입력하세요"
        )
        
        description = st.text_area(
            "문서 설명",
            placeholder="이 문서에 대한 간단한 설명을 입력하세요...",
            height=100,
            help="문서의 내용이나 목적을 설명하세요"
        )
        
        # 업로드 버튼
        if st.button("🚀 업로드 및 학습 시작", type="primary", use_container_width=True):
            upload_documents(doc_manager, uploaded_files, {
                "category": category,
                "department": department,
                "tags": tags,
                "description": description
            })

def upload_documents(doc_manager, files: List, metadata: Dict[str, str]):
    """문서 업로드 실행"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    total_files = len(files)
    successful_uploads = 0
    failed_uploads = []
    
    for i, file in enumerate(files):
        status_text.text(f"📤 업로드 중: {file.name} ({i+1}/{total_files})")
        progress = (i) / total_files
        progress_bar.progress(progress)
        
        try:
            # 파일 내용 읽기
            file_content = file.getvalue()
            
            # 파일 크기 제한 검사 (10MB)
            if len(file_content) > 10 * 1024 * 1024:
                failed_uploads.append((file.name, ["파일 크기가 10MB를 초과합니다"]))
                st.error(f"❌ {file.name}: 파일 크기 초과")
                continue
            
            # 메타데이터 준비 (안전한 문자열만 사용)
            file_metadata = {}
            try:
                for key, value in metadata.items():
                    safe_key = str(key).encode('ascii', errors='ignore').decode('ascii')
                    safe_value = str(value).encode('ascii', errors='ignore').decode('ascii')
                    if safe_key and safe_value:
                        file_metadata[safe_key] = safe_value
                
                # 기본 메타데이터 추가
                file_metadata.update({
                    "file_type": str(file.type or "unknown"),
                    "upload_timestamp": datetime.now().isoformat(),
                    "uploader": "streamlit_user"
                })
            except Exception as meta_error:
                print(f"메타데이터 준비 경고: {meta_error}")
                file_metadata = {
                    "upload_timestamp": datetime.now().isoformat(),
                    "uploader": "streamlit_user"
                }
            
            # 업로드 실행
            result = doc_manager.upload_training_document(
                file_content=file_content,
                filename=file.name,
                metadata=file_metadata
            )
            
            if result["success"]:
                successful_uploads += 1
                st.success(f"✅ {file.name} 업로드 완료")
            else:
                failed_uploads.append((file.name, result.get("errors", ["Unknown error"])))
                st.error(f"❌ {file.name} 업로드 실패")
            
            time.sleep(0.5)  # 시각적 효과
            
        except Exception as e:
            failed_uploads.append((file.name, [str(e)]))
            st.error(f"❌ {file.name} 처리 중 오류: {str(e)}")
    
    # 완료
    progress_bar.progress(1.0)
    status_text.text("✅ 업로드 완료!")
    
    # 결과 요약
    with results_container.container():
        st.markdown("---")
        st.markdown("### 📊 업로드 결과")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("전체 파일", total_files)
        
        with col2:
            st.metric("성공", successful_uploads, delta=f"{(successful_uploads/total_files)*100:.0f}%")
        
        with col3:
            st.metric("실패", len(failed_uploads))
        
        if failed_uploads:
            st.markdown("#### ❌ 업로드 실패 파일")
            for filename, errors in failed_uploads:
                with st.expander(f"❌ {filename}"):
                    for error in errors:
                        st.error(f"오류: {error}")
        
        if successful_uploads > 0:
            st.success(f"🎉 {successful_uploads}개 문서가 성공적으로 학습되었습니다!")
            st.info("업로드된 문서들은 이제 AI 분석에서 참조할 수 있습니다.")

def render_training_documents_list(doc_manager):
    """학습된 문서 목록"""
    st.markdown("### 📋 학습된 문서 관리")
    
    # 검색 기능
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "문서 검색",
            placeholder="파일명, 내용, 키워드로 검색...",
            key="training_docs_search"
        )
    
    with col2:
        if st.button("🔄 목록 새로고침", use_container_width=True, key="refresh_training_docs"):
            # 모든 관련 캐시 클리어하여 강제 새로고침
            cache_keys_to_clear = [
                'training_docs_cache', 
                'training_docs_list', 
                'document_search_cache',
                'last_search_query',
                'training_docs_search'
            ]
            
            for cache_key in cache_keys_to_clear:
                if cache_key in st.session_state:
                    del st.session_state[cache_key]
            
            # 검색 입력 초기화
            st.session_state['training_docs_search'] = ""
            
            st.success("🔄 목록을 새로고침했습니다!")
            time.sleep(0.5)
            st.rerun()
    
    # 문서 목록 가져오기
    with st.spinner("📚 문서 목록을 불러오는 중..."):
        if search_query and search_query.strip():
            documents = doc_manager.search_training_documents(search_query.strip())
        else:
            documents = doc_manager.list_training_documents()
    
    if not documents:
        st.info("📝 학습된 문서가 없습니다. 위의 '문서 업로드' 탭에서 문서를 업로드해주세요.")
        return
    
    # 통계 정보
    stats = doc_manager.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 문서 수", len(documents))
    
    with col2:
        total_size = sum(doc.get("file_size", 0) for doc in documents)
        size_mb = total_size / (1024 * 1024)
        st.metric("총 크기", f"{size_mb:.1f} MB")
    
    with col3:
        storage_available = stats.get("storage_available", False)
        st.metric("Storage 상태", "✅ 연결됨" if storage_available else "❌ 비연결")
    
    with col4:
        search_available = stats.get("search_available", False) 
        st.metric("Search 상태", "✅ 연결됨" if search_available else "❌ 비연결")
    
    st.markdown("---")
    
    # 문서 목록 표시
    for i, doc in enumerate(documents):
        with st.expander(f"📄 {doc['title']} ({doc.get('file_size', 0):,} bytes)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**파일명:** {doc['filename']}")
                st.markdown(f"**업로드일:** {format_date(doc['upload_date'])}")
                
                if doc.get('keywords'):
                    st.markdown(f"**키워드:** {doc['keywords']}")
                
                if doc.get('summary'):
                    st.markdown(f"**요약:** {doc['summary']}")
                
                st.markdown(f"**소스:** {doc.get('source', 'Unknown')}")
            
            with col2:
                # 액션 버튼들
                if st.button(f"🔍 내용 보기", key=f"view_{doc['file_id']}"):
                    show_document_content(doc_manager, doc)
                
                if st.button(f"💬 AI 분석", key=f"analyze_{doc['file_id']}"):
                    st.session_state['selected_text'] = doc.get('summary', doc['title'])
                    st.session_state['ai_panel_open'] = True
                    st.success("AI 패널에서 이 문서로 분석을 시작합니다.")
                
                if st.button(f"🗑️ 삭제", key=f"delete_{doc['file_id']}", type="secondary"):
                    if st.session_state.get(f'confirm_delete_{doc["file_id"]}', False):
                        delete_result = doc_manager.delete_document(doc['file_id'])
                        if delete_result['success']:
                            st.success(f"✅ '{doc['title']}' 삭제 완료")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ 삭제 실패: {', '.join(delete_result['errors'])}")
                    else:
                        st.session_state[f'confirm_delete_{doc["file_id"]}'] = True
                        st.warning("⚠️ 다시 한번 클릭하면 삭제됩니다.")

def show_document_content(doc_manager, doc):
    """문서 내용 표시"""
    st.markdown(f"### 📖 문서 내용: {doc['title']}")
    
    with st.spinner("문서 내용을 불러오는 중..."):
        content = doc_manager.get_document_content(doc['file_id'])
    
    if content:
        # 내용 길이에 따라 표시 방식 결정
        if len(content) > 2000:
            st.markdown("**내용 미리보기 (처음 2000자):**")
            st.text_area("문서 내용", content[:2000] + "\n\n... (더 많은 내용이 있습니다)", height=300, disabled=True)
            
            # 전체 내용 다운로드 링크
            st.download_button(
                label="📄 전체 내용 다운로드",
                data=content,
                file_name=doc['filename'],
                mime="text/plain"
            )
        else:
            st.text_area("문서 내용", content, height=400, disabled=True)
        
        # AI 분석 버튼
        if st.button("🤖 이 내용으로 AI 분석하기", key=f"ai_analyze_content_{doc['file_id']}"):
            st.session_state['selected_text'] = content[:1000] if len(content) > 1000 else content
            st.session_state['ai_panel_open'] = True
            st.success("선택된 내용으로 AI 분석을 시작합니다.")
    else:
        st.error("문서 내용을 불러올 수 없습니다.")

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